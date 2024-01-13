import os
import datetime as dt
import json
import logging
import requests
from dotenv import load_dotenv
from distutils.util import strtobool

class Firefly_Client:
    def __init__(self, portfolio):
        # Create a logger object
        self.logger = logging.getLogger(__name__)
        # Set the logging level
        self.logger.setLevel(logging.INFO)
        # Add a handler to the logger object
        self.handler = logging.StreamHandler()
        self.logger.addHandler(self.handler)
        
        # Firefly III API URL http://myfireflyserver/api
        self.FF_API_URL = os.getenv('FF_API_URL')

        # Firefly III Personal Access Token - https://yourfireflyserver/profile under the OAuth tab
        self.FF_TOKEN = os.getenv('FF_TOKEN')

        # Required Firefly III API Call Configuration Options
        # https://api-docs.firefly-III.org/
        self.FF_ERROR_IF_DUPLICATE_HASH = strtobool(os.getenv('FF_ERROR_IF_DUPLICATE_HASH'))
        self.FF_APPLY_RULES = strtobool(os.getenv('FF_APPLY_RULES'))
        self.FF_FIRE_WEBHOOKS = strtobool(os.getenv('FF_FIRE_WEBHOOKS'))

    # Function for processing the raw data received from Plaid
    def process_transactions(self, new_transactions, account, first_time_sync):
        self.logger.info('Firefly III is Processing Transactions')

        # Initialize variables for Firefly payload
        ff_withdrawals = []
        ff_deposits = []

        # Initialize variable for tracking the oldest transaction date, used to initialize balances if needed
        oldest_group_transaction = dt.date.today()

        for transaction in new_transactions:
            # Check if this transaction is for the account we're processing
            if account['pl_id'] == transaction['account_id']:
                # Create a firefly transaction JSON object with basic details for assembly
                ff_transaction = {}
                ff_transaction['date'] = str(transaction['date'])
                # If this is the first time sync, update the variable for tracking the oldest transaction
                if first_time_sync:
                    if transaction['date'] < oldest_group_transaction:
                        oldest_group_transaction = transaction['date']
                ff_transaction['description'] = transaction['name']
                # Use category from Plaid or bank as is
                ff_transaction['category_name'] = transaction['personal_finance_category']['primary']
                ff_transaction['external_id'] = transaction['transaction_id']
                # Check for external_url
                if transaction['website'] != None:
                    ff_transaction['external_url'] = f"https://{transaction['website']}"
                # Check for location
                if transaction['location']['lat'] != None:
                    ff_transaction['latitude'] = transaction['location']['lat']
                    ff_transaction['longitude'] = transaction['location']['lon']
                # Create a string to assemble and send as a note
                note = ''
                # Check if merchant name is null
                if transaction['merchant_name'] != None:
                    note = f"{transaction['merchant_name']} - "
                # Finalize note and attach to transaction
                ff_transaction['note'] = f"{note}Category Confidence: {transaction['personal_finance_category']['confidence_level']} - {transaction['personal_finance_category']['detailed']}"
                # Determine withdrawal or deposit, positive amounts are considered withdrawals
                if transaction['amount'] > 0:
                    ff_transaction['type'] = 'withdrawal' 
                    ff_transaction['amount'] = str(transaction['amount'])
                    ff_transaction['source_id'] = account['ff_id']
                    ff_transaction['source_name'] = account['ff_name']
                    ff_withdrawals.append(ff_transaction)
                # Negative amounts are considered deposits, Firefly requires an absolute value regardless of type
                if transaction['amount'] < 0:
                    ff_transaction['type'] = 'deposit'
                    ff_transaction['amount'] = str(abs(transaction['amount']))
                    ff_transaction['destination_id'] = account['ff_id']
                    ff_transaction['destination_name'] = account['ff_name']
                    ff_deposits.append(ff_transaction)

        # Send batches of transactions to Firefly
        self.sync_transactions(ff_withdrawals)
        self.sync_transactions(ff_deposits)

        return oldest_group_transaction

    # Function to send transactions to Firefly III
    def sync_transactions(self, payload):
        self.logger.info('Syncing transactions to firefly')
        self.logger.info('Payload length:')
        self.logger.info(len(payload))

        # Prepare base Firefly Request
        ff_request = {}
        ff_request['error_if_duplicate_hash'] = self.FF_ERROR_IF_DUPLICATE_HASH
        ff_request['apply_rules'] = self.FF_APPLY_RULES
        ff_request['fire_webhooks'] = self.FF_FIRE_WEBHOOKS
        # Name batch "Plaid Sync - 2024-12-31"
        ff_request['group_title'] = f"Plaid Sync - {dt.datetime.now()}"
        ff_headers = {'accept':'application/vnd.api+json','Content-Type':'application/json','Authorization':self.FF_TOKEN}
        # Add transactions payload to request
        ff_request['transactions'] = payload
        # Send transactions payload to Firefly
        response = requests.post(f"{self.FF_API_URL}/v1/transactions",json=ff_request,headers=ff_headers)
        self.logger.info('Firefly Request:')
        self.logger.info(response.json())

    def sync_balances(self, account, balance, oldest_transaction):
        # Handle syncing balances here
        self.logger.info(f"Oldest transaction returned for {account['ff_name']} was on {oldest_transaction}.")

        # Fetch current account info from Firefly
        ff_headers = {'accept':'application/vnd.api+json','Authorization':self.FF_TOKEN}
        response = requests.get(f"{self.FF_API_URL}/v1/accounts/{account['ff_id']}",headers=ff_headers)

        # Initialize Firefly account object
        ff_account = response.json()['data']['attributes']
        ff_balance = float(ff_account['current_balance'])

        # Check for discrepencies
        if not ff_balance == balance:
            initial_balance = 0
            # If the account is a liability the balance from Plaid needs to be negative to properly compare
            if account['type'] == 'liability':
                balance = -abs(balance)
            self.logger.info(f'Balance discrepency detected, balance from Plaid: {balance}, balance in Firefly III: {ff_account['current_balance']}')
            # Calculate difference
            initial_balance = balance - ff_balance
            initial_balance_date = oldest_transaction - dt.timedelta(days=1)
            self.logger.info(f'Adjusting initial balance to: {initial_balance}, on {initial_balance_date}')
            # Initialize payload
            ff_balance_sync = []
            ff_transaction = {}
            ff_transaction['date'] = str(initial_balance_date)
            ff_transaction['description'] = "Initial balance"
            ff_transaction['category_name'] = "INITIAL_BALANCE"
            # This time we need to invert the normal withdrawal/deposit logic
            if initial_balance < 0:
                ff_transaction['type'] = 'withdrawal' 
                ff_transaction['amount'] = str(abs(initial_balance))
                ff_transaction['source_id'] = account['ff_id']
                ff_transaction['source_name'] = account['ff_name']
                ff_balance_sync.append(ff_transaction)
            # Negative amounts are considered deposits, Firefly requires an absolute value regardless of type
            if initial_balance > 0:
                ff_transaction['type'] = 'deposit'
                ff_transaction['amount'] = str(abs(initial_balance))
                ff_transaction['destination_id'] = account['ff_id']
                ff_transaction['destination_name'] = account['ff_name']
                ff_balance_sync.append(ff_transaction)

            # Sending transactions to Firefly
            self.sync_transactions(ff_balance_sync)