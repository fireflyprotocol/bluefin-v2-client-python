from .contract_abis import MarginBank, Perpetual, USDC
from .enumerations import *
class Contracts:
    def __init__(self):
        self.contracts = {}
        self.contract_addresses = {}
        
    def set_contract_addresses(self,contract_address,market=None,name=None):
        self.contract_addresses["auxiliaryContractsAddresses"]=contract_address['auxiliaryContractsAddresses']
        self.contract_addresses[market]=contract_address[market.value]
    

    def get_perpetual_id(self, market: MARKET_SYMBOLS=MARKET_SYMBOLS.ETH):
        return self.contract_addresses[market]['Perpetual']['id']
    def get_package_id(self, market: MARKET_SYMBOLS=MARKET_SYMBOLS.ETH):
        return self.contract_addresses[market]['package']['id']
    
    def get_currency_type(self):
        return self.contract_addresses['auxiliaryContractsAddresses']['objects']['Currency']['dataType']
    
    def get_bank_id(self, market: MARKET_SYMBOLS=MARKET_SYMBOLS.ETH):
        return self.contract_addresses['auxiliaryContractsAddresses']['objects']['Bank']['id']
    def get_contract(self,name,market=""):
        """
            Returns the contract object.
            Inputs:
                - name(str): The contract name.
                - market(str): The market the contract belongs to (required for market specific contracts).
        """
        try:
            if name in self.contracts.keys():
                return self.contracts[name]
            if market in self.contracts.keys() and name in self.contracts[market].keys():
                return self.contracts[market][name]
            else:
                return "Contract not found"
        except Exception as e:
            raise(Exception("Failed to get contract, Exception: {}".format(e)))

    def get_contract_address(self,name=None,market=None):
        """
            Returns the contract address. If neither of the inputs provided, will return a dict with all contract addresses.  
            Inputs:
                - name(str): The contract name.
                - market(str): The market the contract belongs to (if only market provided will return all address of market as dict).
        """
        try:
            if market and name:
                return self.contract_addresses[market][name]
            elif market:
                return self.contract_addresses[market]
            elif name:
                return self.contract_addresses["auxiliaryContractsAddresses"][name]
            else:
                return self.contract_addresses
        except Exception as e:
            raise(Exception("Failed to get contract address, Exception: {}".format(e)))
        

        
    def get_market_id(self,market: str)-> str:
        """
            Returns the market id/Perpetual ID for the respective market.
            Inputs: 
                - market(str) the name of the market for which you need perp id e.g ETH-PERP
        """
        return self.contract_addresses[market.value]['Perpetual']['id']


    
