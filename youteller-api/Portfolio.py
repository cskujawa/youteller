import os
from dotenv import load_dotenv

class Portfolio:
    def __init__(self):
        # Instantiate Portfolio
        self.accounts = []

        # Assemble bank objects matching Plaid Access Tokens and Account IDs to Firefly III Bank Name and IDs
        # Bank one
        self.bank = {}
        self.bank['type'] = 'bank'
        self.bank['access_token'] = os.getenv('PLAID_BANK_1_ACCESS_TOKEN')
        self.bank['pl_id'] = os.getenv('PLAID_BANK_1_ID')
        self.bank['ff_id'] = os.getenv('FF_BANK_1_ID')
        self.bank['ff_name'] = os.getenv('FF_BANK_1_NAME')
        self.bank['cursor'] = ''
        self.accounts.append(self.bank)
        # Bank two
        self.bank = {}
        self.bank['type'] = 'bank'
        self.bank['access_token'] = os.getenv('PLAID_HYS_1_ACCESS_TOKEN')
        self.bank['pl_id'] = os.getenv('PLAID_HYS_1_ID')
        self.bank['ff_id'] = os.getenv('FF_HYS_1_ID')
        self.bank['ff_name'] = os.getenv('FF_HYS_1_NAME')
        self.bank['cursor'] = ''
        self.accounts.append(self.bank)

        # Assemble liabilities objects matching Plaid Access Tokens and Account IDs to Firefly III Bank Name and IDs
        # Liability one
        self.liability = {}
        self.liability['type'] = 'liability'
        self.liability['access_token'] = os.getenv('PLAID_CC_1_ACCESS_TOKEN')
        self.liability['pl_id'] = os.getenv('PLAID_CC_1_ID')
        self.liability['ff_id'] = os.getenv('FF_CC_1_ID')
        self.liability['ff_name'] = os.getenv('FF_CC_1_NAME')
        self.liability['cursor'] = ''
        self.accounts.append(self.liability)
        # Liability two
        self.liability = {}
        self.liability['type'] = 'liability'
        self.liability['access_token'] = os.getenv('PLAID_CC_2_ACCESS_TOKEN')
        self.liability['pl_id'] = os.getenv('PLAID_CC_2_ID')
        self.liability['ff_id'] = os.getenv('FF_CC_2_ID')
        self.liability['ff_name'] = os.getenv('FF_CC_2_NAME')
        self.liability['cursor'] = ''
        self.accounts.append(self.liability)
        # Liability three
        self.liability = {}
        self.liability['type'] = 'liability'
        self.liability['access_token'] = os.getenv('PLAID_CC_3_ACCESS_TOKEN')
        self.liability['pl_id'] = os.getenv('PLAID_CC_3_ID')
        self.liability['ff_id'] = os.getenv('FF_CC_3_ID')
        self.liability['ff_name'] = os.getenv('FF_CC_3_NAME')
        self.liability['cursor'] = ''
        self.accounts.append(self.liability)
        # Liability four
        self.liability = {}
        self.liability['type'] = 'liability'
        self.liability['access_token'] = None
        self.liability['pl_id'] = None
        self.liability['ff_id'] = os.getenv('FF_AUTO_LOAN_1_ID')
        self.liability['ff_name'] = os.getenv('FF_AUTO_LOAN_1_NAME')
        self.liability['cursor'] = ''
        self.accounts.append(self.liability)
        # Liability five
        self.liability = {}
        self.liability['type'] = 'liability'
        self.liability['access_token'] = None
        self.liability['pl_id'] = None
        self.liability['ff_id'] = os.getenv('FF_MORTGAGE_1_ID')
        self.liability['ff_name'] = os.getenv('FF_MORTGAGE_1_NAME')
        self.liability['cursor'] = ''
        self.accounts.append(self.liability)

        # Assemble investments objects matching Plaid Access Tokens and Account IDs to Firefly III Bank Name and IDs
        # Investment one
        self.investment = {}
        self.investment['type'] = 'investment'
        self.investment['access_token'] = os.getenv('PLAID_401k_1_ACCESS_TOKEN')
        self.investment['pl_id'] = os.getenv('PLAID_401k_1_ID')
        self.investment['ff_id'] = os.getenv('FF_401k_1_ID')
        self.investment['ff_name'] = os.getenv('FF_401k_1_NAME')
        self.investment['cursor'] = ''
        self.accounts.append(self.investment)