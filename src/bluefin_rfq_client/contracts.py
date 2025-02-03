from typing import Dict, List, Any

class RFQContracts:
    def __init__(self, contract_config: Dict[str, Any]) -> None:
        """
        Initialize the RFQContracts instance with contract addresses and vaults.

        :param contract_data: Dictionary containing contract addresses and vaults.
        """
        self.contract_data = contract_config
    
    def get_protocol_config(self) -> str:
        return self.contract_data["ProtocolConfig"]
    
    def get_admin_cap(self) -> str:
        return self.contract_data["AdminCap"]
    
    def get_package(self) -> str:
        return self.contract_data["Package"]
    
    def get_upgrade_cap(self) -> str:
        return self.contract_data["UpgradeCap"]
    
    def get_base_package(self) -> str:
        return self.contract_data["BasePackage"]
    
    def get_vaults(self) -> List[str]:
        return self.contract_data.get("vaults", [])
