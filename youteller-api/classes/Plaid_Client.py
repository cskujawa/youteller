import os
import datetime as dt
import json
import logging
import requests
from dotenv import load_dotenv
import plaid
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.api import plaid_api

class Plaid_Client:
    def __init__(self, portfolio):
        # Create a logger object
        self.logger = logging.getLogger(__name__)
        # Set the logging level
        self.logger.setLevel(logging.INFO)
        # Add a handler to the logger object
        self.handler = logging.StreamHandler()
        self.logger.addHandler(self.handler)

        # Plaid Client ID and Secret from your developer account
        PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
        PLAID_SECRET = os.getenv('PLAID_SECRET')

        # Plaid environment, either development or production
        PLAID_ENV = os.getenv('PLAID_ENV')

        # Plaid Host Initialization
        host = plaid.Environment.Development
        if PLAID_ENV == 'development':
            host = plaid.Environment.Development
        if PLAID_ENV == 'production':
            host = plaid.Environment.Production

        # Initialize Plaid cursor position on server load
        for account in portfolio:
            # Check if the account has a Plaid ID (note that some Plaid items do not have an account_id, for these set the PLAID_ID in .env to "no-id")
            if account['pl_id'] is not None:
                # Cursor positions are written to file using the FF_ID as the file name, if one does not exist it will be made in the /cursor/ folder which needs to exist
                if not os.path.isfile(f"/opt/app/youteller-api/cursors/{account['ff_id']}"):
                    self.logger.info('Creating cursor files')
                    file = open(f"/opt/app/youteller-api/cursors/{account['ff_id']}",'w')
                    file.write('')
                    file.close()
                # Read cursor position from file
                self.logger.info('Reading cursor files')
                file = open(f"/opt/app/youteller-api/cursors/{account['ff_id']}",'r')
                account['cursor'] = file.read()
                file.close()

        # Define configuration for Plaid API client
        configuration = plaid.Configuration(
            host=host,
            api_key={
                'clientId': PLAID_CLIENT_ID,
                'secret': PLAID_SECRET,
                'plaidVersion': '2020-09-14'
            }
        )

        # Initiate new Plaid API Client 
        api_client = plaid.ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)

    def transaction_sync(self, account, firefly):
        # Initialize variables to hold new transactions since the cursor position and check for more
        added = []
        has_more = True
        # Check if this is the first time the bank has been synced, if there is no cursor position it is considered new
        # Since transactional history does not account for initial balances
        # We will need to track the oldest transaction returned and initiatlize balances the day before
        oldest_transaction = dt.date.today()
        first_time_sync = False
        if account['cursor'] == '':
            self.logger.info('First time sync detected, initial balances to be determined')
            first_time_sync = True

        try:
            # Iterate through each page of new transaction updates for item
            while has_more:
                request = TransactionsSyncRequest(
                    access_token=account['access_token'],
                    cursor=account['cursor'],
                )
                response = self.client.transactions_sync(request).to_dict()
                # Add this page of results
                added.extend(response['added'])
                # See if there is more
                has_more = response['has_more']
                # Update cursor to the next cursor
                account['cursor'] = response['next_cursor']

                # Log out the length of returned transactions
                self.logger.info(f'New transactions to process for {account['ff_name']}: {len(response['added'])}')

                # If there is transactions to sync, process them through the Firefly_Client.py (note that the function returns the oldest transaction date)
                if len(response['added']):
                    oldest_transaction = firefly.process_transactions(response['added'], account, first_time_sync)

            # Write ending cursor position to file
            file = open(f"/opt/app/youteller-api/cursors/{account['ff_id']}",'w')
            file.write(str(account['cursor']))
            file.close()

        except plaid.ApiException as e:
            error_response = self.format_error(e)
            return jsonify(error_response)

        # Check if this is the first time syncing, if it is sync the balances through the Firefly_Client.py
        if first_time_sync:
            balance = self.get_balance(account)
            firefly.sync_balances(account, balance, oldest_transaction)

    # Retrieve real-time balance data for each of an Item's accounts
    # https://plaid.com/docs/#balance
    def get_balance(self, account):
        try:
            request = AccountsBalanceGetRequest(
                access_token=account['access_token']
            )
            response = self.client.accounts_balance_get(request).to_dict()
            self.logger.info("balance from plaid")
            self.logger.info(response)

            # Plaid access tokens may include multiple accounts, this for-if loop ensures we only return relevant data
            for acc in response['accounts']:
                # Check for account_id match, or for some Plaid accounts check for 'no-id'
                if acc['account_id'] == account['pl_id'] or account['pl_id'] == 'no-id':
                    self.logger.info("in get_balance, account ID matches PL ID")
                    return float(acc['balances']['current'])
        except plaid.ApiException as e:
            error_response = self.format_error(e)
            return jsonify(error_response)

    def format_error(self, e):
        response = json.loads(e.body)
        return {'error': {'status_code': e.status, 'display_message':
                        response['error_message'], 'error_code': response['error_code'], 'error_type': response['error_type']}}