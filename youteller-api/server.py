import base64
import os
import datetime as dt
import json
import time
import logging
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# Import portfolio module
import Portfolio

# Import classes
import sys
sys.path.append("classes")
import Plaid_Client
import Firefly_Client

# Load environment variables
load_dotenv()

################
# Initialize app
app = Flask(__name__)

# Create a logger object
logger = logging.getLogger(__name__)
# Set the logging level
logger.setLevel(logging.INFO)
# Add a handler to the logger object
handler = logging.StreamHandler()
logger.addHandler(handler)

# Initiate Portfolio
portfolio = Portfolio.Portfolio()

# Initiate Plaid Controller
plaid = Plaid_Client.Plaid_Client(portfolio.accounts)

# Initiate Firefly Controller
firefly = Firefly_Client.Firefly_Client(portfolio.accounts)

# Endpoint used by Firefly III to sync transactions, new accounts will have their balances synced
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    for account in portfolio.accounts:
        # Currently this endpoint will only fetch Plaid transactions, validate on pl_id
        if account['pl_id'] is not None:
            plaid.transaction_sync(account, firefly)

    return "200"

# Calculate Interest Function
#
# Put code here

if __name__ == '__main__':
    app.run(port=int(os.getenv('PORT', 8000)))