from typing import Dict, List, Any

class RFQContracts:
    def __init__(self, contract_config: Dict[str, Any]) -> None:
        """
        Initialize the RFQContracts instance with contract addresses and vaults.

        :param contract_config: Dictionary containing contract addresses and vaults.

        Returns:
        instance of RFQContracts
        """
        self.contract_config = contract_config
    
    def get_protocol_config(self) -> str:
        """
        Returns object ID for on-chain object holding protocol configurations.
        """
        return self.contract_config["ProtocolConfig"]
    
    def get_admin_cap(self) -> str:
        """
        Returns object ID for on-chain admin cap object, owned by protocol admin.
        """
        return self.contract_config["AdminCap"]
    
    def get_package(self) -> str:
        """
        Returns package ID for on-chain protocol contracts.
        """
        return self.contract_config["Package"]
    
    def get_upgrade_cap(self) -> str:
        """
        Returns upgrade ID for on-chain upgrade cap object owned by protocol admin.
        """
        return self.contract_config["UpgradeCap"]
    
    def get_base_package(self) -> str:
        """
        Returns base package ID of the protocol.
        """
        return self.contract_config["BasePackage"]
    
    def get_vaults(self) -> List[str]:
        """
        Returns the available RFQ vaults.
        """
        return self.contract_config.get("vaults", [])
