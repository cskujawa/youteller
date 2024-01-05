# source /Users/tnappy/node_projects/quickstart/python/bin/activate
# Read env vars from .env file
import base64
import os
import datetime as dt
import json
import time
import logging
import requests
import pickle

from dotenv import load_dotenv
from dotenv import set_key
from flask import Flask, request, jsonify
import plaid
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.api import plaid_api

# Load environment variables
load_dotenv()

#########
# Firefly III Specific Variables
# Firefly III API URL 
# i.e. http://myfireflyserver/api
FF_API_URL = os.getenv('FF_API_URL')

# Firefly iii Personal Access Token - https://yourfireflyserver/profile under the OAuth tab
FF_TOKEN = os.getenv('FF_TOKEN')

# Required Firefly iii API Call Configuration Options
# https://api-docs.firefly-iii.org/
FF_ERROR_IF_DUPLICATE_HASH = os.getenv('FF_ERROR_IF_DUPLICATE_HASH')
FF_APPLY_RULES = os.getenv('FF_APPLY_RULES')
FF_FIRE_WEBHOOKS = os.getenv('FF_FIRE_WEBHOOKS')

# Firefly iii Bank IDs & Names
# These must match to their corresponding Plaid BANK_#_ID
FF_BANK_1_ID = os.getenv('FF_BANK_1_ID')
FF_BANK_1_NAME = os.getenv('FF_BANK_1_NAME')
FF_BANK_2_ID = os.getenv('FF_BANK_2_ID')
FF_BANK_2_NAME = os.getenv('FF_BANK_2_NAME')

#########
# Plaid Specific Variables
# Fill in your Plaid API keys - https://dashboard.plaid.com/account/keys
# Client ID must be a developer access key
# Developer keys work for up to 100 live bank accounts and are completely free
# https://plaid.com/docs/quickstart/#introduction
PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')

# Plaid environment, either development or production
PLAID_ENV = os.getenv('PLAID_ENV')

# Plaid Bank Access Tokens
# This app does not handle auth or account management through Plaid
# It is assumed you already have an access_token and item_id as seen in:
# https://github.com/plaid/quickstart/blob/master/assets/quickstart.jpeg
BANK_1_ACCESS_TOKEN = os.getenv('BANK_1_ACCESS_TOKEN')
BANK_2_ACCESS_TOKEN = os.getenv('BANK_2_ACCESS_TOKEN')

# Assemble bank objects
banks = []
bank = {}
bank['access_token'] = BANK_1_ACCESS_TOKEN
bank['ff_id'] = FF_BANK_1_ID
bank['ff_name'] = FF_BANK_1_NAME
bank['cursor'] = ''
banks.append(bank)
bank = {}
bank['access_token'] = BANK_2_ACCESS_TOKEN
bank['ff_id'] = FF_BANK_2_ID
bank['ff_name'] = FF_BANK_2_NAME
bank['cursor'] = ''
banks.append(bank)
    
################
# Initialize app
app = Flask(__name__)

# Plaid Host Initializatin
host = plaid.Environment.Development
if PLAID_ENV == 'development':
    host = plaid.Environment.Development
if PLAID_ENV == 'production':
    host = plaid.Environment.Production

# Create a logger object
logger = logging.getLogger(__name__)
# Set the logging level
logger.setLevel(logging.INFO)
# Add a handler to the logger object
handler = logging.StreamHandler()
logger.addHandler(handler)

# Initialize cursor position from file
for bank in banks:
    # If cursor file doesn't exist create one
    if not os.path.isfile(f"/opt/app/youteller-api/cursors/{bank['ff_id']}"):
        logger.info('Creating cursor files')
        file = open(f"/opt/app/youteller-api/cursors/{bank['ff_id']}",'w')
        file.write('')
        file.close()
    # Read cursor position from file
    logger.info('Reading cursor files')
    file = open(f"/opt/app/youteller-api/cursors/{bank['ff_id']}",'r')
    bank['cursor'] = file.read()
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
client = plaid_api.PlaidApi(api_client)


# Retrieve Transactions for an Item
# https://plaid.com/docs/#transactions
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    for bank in banks:
        plaid_transaction_sync(bank)

    return "200"

def plaid_transaction_sync(bank):
    # New transaction updates since "cursor"
    added = []
    has_more = True
    # Check if this is the first time the bank has been synced
    # Since transactional history does not account for initial balances
    # We will need to track the oldest transaction returned and initiatlize balances the day before
    oldest_transaction = dt.date.today()
    first_time_sync = False
    if bank['cursor'] == '':
        logger.info('First time sync detected, initial balances to be determined')
        first_time_sync = True

    try:
        # Iterate through each page of new transaction updates for item
        while has_more:
            request = TransactionsSyncRequest(
                access_token=bank['access_token'],
                cursor=bank['cursor'],
            )
            response = client.transactions_sync(request).to_dict()
            # Add this page of results
            added.extend(response['added'])
            has_more = response['has_more']
            # Update cursor to the next cursor
            bank['cursor'] = response['next_cursor']

            # Log out the length of returned transactions
            logger.info('Added: ')
            logger.info(len(response['added']))

            # Process transactions
            if len(response['added']):
                oldest_transaction = process_transactions(response['added'], bank, first_time_sync)

        # Write ending cursor position to file
        file = open(f"/opt/app/youteller-api/cursors/{bank['ff_id']}",'w')
        file.write(str(bank['cursor']))
        file.close()

    except plaid.ApiException as e:
        error_response = format_error(e)
        return jsonify(error_response)

    if first_time_sync:
        sync_balances(bank, oldest_transaction)

def sync_balances(bank, oldest_transaction):
    # Handle syncing balances here
    logger.info(f"Oldest transaction returned for {bank['ff_name']} was on {oldest_transaction}.")

    # Fetch current account info from Firefly
    ff_headers = {'accept':'application/vnd.api+json','Authorization':FF_TOKEN}
    response = requests.get(f"{FF_API_URL}/v1/accounts/{bank['ff_id']}",headers=ff_headers)
    logger.info('Firefly Account Request:')
    logger.info(response.json())

    # Initialize Firefly account object
    account = response.json()['data']['attributes']
    logger.info(f"Current Balance: {account['current_balance']}")
    logger.info(f"Opening Balance: {account['opening_balance']}")
    logger.info(f"Opening Balance Date: {account['opening_balance_date']}")
    ff_balance = float(account['current_balance'])

    # Fetch current balances from Plaid
    plaid_balance = get_balance(bank)
    logger.info("Balance from Plaid:")
    logger.info(plaid_balance)

    # Check for discrepencies
    if not ff_balance == plaid_balance:
        logger.info('Balance discrepency detected attempting rectification')
        initial_balance = 0
        if ff_balance < plaid_balance:
            initial_balance = plaid_balance - ff_balance
            logger.info(f'Initial Balance: {initial_balance}')
            initial_balance_date = oldest_transaction - dt.timedelta(days=1)
            logger.info(f'Initial Balance Date: {initial_balance_date}')

            # Instantiate Firefly payload
            ff_account_payload = {}
            # Assemble payload
            ff_account_payload['active'] = account['active']
            ff_account_payload['name'] = account['name']
            ff_account_payload['account_role'] = account['account_role']
            ff_account_payload['currency_id'] = account['currency_id']
            ff_account_payload['currency_code'] = account['currency_code']
            ff_account_payload['notes'] = account['notes'] 
            ff_account_payload['monthly_payment_date'] = account['monthly_payment_date']
            ff_account_payload['credit_card_type'] = account['credit_card_type']
            ff_account_payload['account_number'] = account['account_number']
            ff_account_payload['iban'] = account['iban']
            ff_account_payload['bic'] = account['bic']
            ff_account_payload['virtual_balance'] = account['virtual_balance']
            ff_account_payload['liability_type'] = account['liability_type']
            ff_account_payload['interest'] = account['interest']
            ff_account_payload['interest_period'] = account['interest_period']
            ff_account_payload['include_net_worth'] = account['include_net_worth']
            # Add opening balance info
            ff_account_payload['opening_balance'] = initial_balance
            ff_account_payload['opening_balance_date'] = str(initial_balance_date)
            logger.info('Assembled account update payload')
            logger.info(ff_account_payload)
            # Scrub none values
            ff_account_payload = {key: value for (key, value) in ff_account_payload.items() if value is not None}
            logger.info('Scrubbed account update payload')
            logger.info(ff_account_payload)
            # Send request to Firefly to update account
            ff_headers = {'accept':'application/vnd.api+json','Content-Type':'application/json','Authorization':FF_TOKEN}
            response = requests.put(f"{FF_API_URL}/v1/accounts/{bank['ff_id']}",json=ff_account_payload,headers=ff_headers)
            logger.info(response)


# Retrieve real-time balance data for each of an Item's accounts
# https://plaid.com/docs/#balance
def get_balance(bank):
    try:
        request = AccountsBalanceGetRequest(
            access_token=bank['access_token']
        )
        response = client.accounts_balance_get(request).to_dict()
        logger.info(response)

        # Skip cheapskate savings accounts if present (checking accounts are second)
        if len(response['accounts']) == 2:
            return response['accounts'][1]['balances']['current']

        return response['accounts'][0]['balances']['current']
    except plaid.ApiException as e:
        error_response = format_error(e)
        return jsonify(error_response)

# Function for processing the raw data received from Plaid
def process_transactions(new_transactions, bank, first_time_sync):
    logger.info('Processing Transactions')

    # Variables for Firefly payload
    ff_withdrawals = []
    ff_deposits = []

    oldest_group_transaction = dt.date.today()

    for transaction in new_transactions:
        # Create a firefly transaction JSON object with basic details for assembly
        ff_transaction = {}
        ff_transaction['date'] = str(transaction['date'])
        if first_time_sync:
            if transaction['date'] < oldest_group_transaction:
                oldest_group_transaction = transaction['date']
        ff_transaction['description'] = transaction['name']
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
            ff_transaction['source_id'] = bank['ff_id']
            ff_transaction['source_name'] = bank['ff_name']
            ff_withdrawals.append(ff_transaction)
        # Negative amounts are considered deposits, Firefly requires an absolute value regardless of type
        if transaction['amount'] < 0:
            ff_transaction['type'] = 'deposit'
            ff_transaction['amount'] = str(abs(transaction['amount']))
            ff_transaction['destination_id'] = bank['ff_id']
            ff_transaction['destination_name'] = bank['ff_name']
            ff_deposits.append(ff_transaction)

    # Sending transactions to Firefly
    sync_to_firefly(ff_withdrawals)
    sync_to_firefly(ff_deposits)

    return oldest_group_transaction

def sync_to_firefly(payload):
    logger.info('Syncing transactions to firefly')
    logger.info('Payload length:')
    logger.info(len(payload))

    # Prepare Firefly Request
    ff_request = {}
    ff_request['error_if_duplicate_hash'] = False
    ff_request['apply_rules'] = True
    ff_request['fire_webhooks'] = False
    ff_request['group_title'] = f"Plaid Sync - {dt.datetime.now()}"
    ff_headers = {'accept':'application/vnd.api+json','Content-Type':'application/json','Authorization':FF_TOKEN}
    # Add transactions payload to request
    ff_request['transactions'] = payload
    # Send transactions payload to Firefly
    response = requests.post(f"{FF_API_URL}/v1/transactions",json=ff_request,headers=ff_headers)
    logger.info('Firefly Request:')
    logger.info(response.json())

def format_error(e):
    response = json.loads(e.body)
    return {'error': {'status_code': e.status, 'display_message':
                      response['error_message'], 'error_code': response['error_code'], 'error_type': response['error_type']}}

if __name__ == '__main__':
    app.run(port=int(os.getenv('PORT', 8000)))