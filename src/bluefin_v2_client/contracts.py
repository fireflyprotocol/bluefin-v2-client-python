from .enumerations import MARKET_SYMBOLS


_DEFAULT_MARKET = "BTC-PERP"


class Contracts:
    def __init__(self):
        self.contracts_global_info = {}
        self.contract_info = {}

    def set_contract_addresses(self, contracts_info):
        self.contract_info = contracts_info
        self.contracts_global_info = contracts_info["auxiliaryContractsAddresses"][
            "objects"
        ]

    def get_sub_account_id(self):
        return self.contracts_global_info["SubAccounts"]["id"]

    def get_bank_table_id(self):
        return self.contracts_global_info["BankTable"]["id"]

    def get_package_id(self):
        return self.contracts_global_info["package"]["id"]

    def get_bank_id(self):
        return self.contracts_global_info["Bank"]["id"]

    def get_currency_type(self):
        return self.contracts_global_info["Currency"]["dataType"]

    def get_price_oracle_object_id(self, market: MARKET_SYMBOLS):
        return self.contract_info[market.value]["PriceOracle"]["id"]

    def get_perpetual_id(self, market: MARKET_SYMBOLS):
        return self.contract_info[market.value]["Perpetual"]["id"]
