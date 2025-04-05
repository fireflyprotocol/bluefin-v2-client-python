from datetime import timezone
from typing import Tuple
from .quote import Quote
from sui_utils import *
from .contracts import RFQContracts

class RFQClient:
    def __init__(self, wallet: SuiWallet  = None , url: str = None, rfq_contracts : RFQContracts = None):
        """
        Initializes the RFQClient instance with provided input fields.

        Inputs:
          wallet (SuiWallet): instance of SuiWallet class.
          url (str): RPC url of chain node (e.g https://fullnode.<SUI-NETWORK-VERSION>.sui.io:443)
          rfq_contracts (RFQContracts): instance of RFQContracts class.

        Output:
          instance of RFQClient.
        """
        if wallet is None:
            raise ValueError(
                "Initialize SuiWallet to use RFQClient")
        if url is None:
            raise ValueError(
                "Please provide rpc url of chain")
        if rfq_contracts is None:
            raise ValueError(
                "Please provide url of chain")
        self.wallet = wallet
        self.url = url
        self.rfq_contracts = rfq_contracts
        self.signer = Signer()

    ###########################################################
    ############## Quote Management Methods ###################
    ###########################################################

    @staticmethod
    def create_quote(
        vault: str,
        quote_id: str,
        taker: str,
        token_in_amount: int,
        token_out_amount: int,
        token_in_type: str,
        token_out_type: str,
        created_at_utc_ms: int | None = None,
        expires_at_utc_ms: int | None = None ) -> Quote:
        """
        Creates an instance of Quote with provided params.

        Inputs:
          vault (str): on chain vault object ID.
          quote_id (str): unique quote ID assigned for on chain verification and security.
          taker (str): address of the reciever account.
          token_in_amount (int): amount of the input token (scaled to supported coin decimals, eg. 1000000000 for 1 Sui).
          token_out_amount (int): amount of the output token (scaled to supported coin decimals, eg. 1000000 for 1 USDC).
          token_in_type (str): on chain token type of input coin, without 0x prefix (i.e for SUI , 0000000000000000000000000000000000000000000000000000000000000002::sui::SUI).
          token_out_type (str): on chain token type of output coin, without 0x prefix (i.e for USDC , dba34672e30cb065b1f93e3ab55318768fd6fef66c15942c9f7cb846e2f900e7::usdc::USDC).
          created_at_utc_ms (int): the unix timestamp at which the quote was created in milliseconds (Defaults to current timestamp).
          expires_at_utc_ms (int): the unix timestamp at which the quote is to be expired in milliseconds (Defaults to 30 seconds after creation timestamp).

        Output:
          instance of Quote Class.
        """

        if created_at_utc_ms is None:
            created_at_utc_ms = int(datetime.now(timezone.utc).timestamp()) * 1000
        if expires_at_utc_ms is None:
            expires_at_utc_ms = created_at_utc_ms + 30000 # 30 seconds expiration

        return Quote(
            vault=vault,
            quote_id=quote_id,
            taker=taker,
            token_in_amount=token_in_amount,
            token_out_amount=token_out_amount,
            token_in_type=token_in_type,
            token_out_type=token_out_type,
            expires_at=expires_at_utc_ms,
            created_at=created_at_utc_ms,
        )
    
    def create_and_sign_quote(
        self, 
        vault: str,
        quote_id: str,
        taker: str,
        token_in_amount: int,
        token_out_amount: int,
        token_in_type: str,
        token_out_type: str,
        created_at_utc_ms: int | None = None,
        expires_at_utc_ms: int | None = None ) -> Tuple[Quote,str]:

        """
        Creates an instance of Quote with provided params and signs it.

        Inputs:
          vault (str): on chain vault object ID.
          quote_id (str): unique quote ID assigned for on chain verification and security.
          taker (str): address of the reciever account.
          token_in_amount (int): amount of the input token (scaled to supported coin decimals, eg. 1000000000 for 1 Sui).
          token_out_amount (int): amount of the output token (scaled to supported coin decimals, eg. 1000000 for 1 USDC).
          token_in_type (str): on chain token type of input coin, without 0x prefix (i.e for SUI , 0000000000000000000000000000000000000000000000000000000000000002::sui::SUI).
          token_out_type (str): on chain token type of output coin, without 0x prefix (i.e for USDC , dba34672e30cb065b1f93e3ab55318768fd6fef66c15942c9f7cb846e2f900e7::usdc::USDC).
          created_at_utc_ms (int): the unix timestamp at which the quote was created in milliseconds (Defaults to current timestamp).
          expires_at_utc_ms (int): the unix timestamp at which the quote is to be expired in milliseconds (Defaults to 30 seconds after creation timestamp).

        Output:
          Tuple of Quote instance and base64 encoded signature.
        """

        if created_at_utc_ms is None:
            created_at_utc_ms = int(datetime.now(timezone.utc).timestamp())
        if expires_at_utc_ms is None:
            expires_at_utc_ms = created_at_utc_ms + 30000 # 30 seconds expiration

        quote = Quote(
            vault=vault,
            id=quote_id,
            taker=taker,
            token_in_amount=token_in_amount,
            token_out_amount=token_out_amount,
            token_in_type=token_in_type,
            token_out_type=token_out_type,
            expires_at=expires_at_utc_ms,
            created_at=created_at_utc_ms,
        )

        signature = quote.sign(self.wallet)
        return (quote, base64.b64encode(signature).decode('utf-8'))
    
    
    ###########################################################
    ############## Vault Management Methods ##################
    ###########################################################
    
    def create_vault(self, 
        manager: str,
        gasbudget: str | None = 100000000
        ) -> tuple[bool, TransactionResult] :
        """
        Creates new vault on bluefin RFQ protocol with provided vault manager.

        Inputs:
          manager (str): address of the account that needs to be manager of vault.
          gasbudget (str, optional): Gas budget for transaction (default: "100000000", 0.1 Sui).

        Output:
          Tuple of bool (indicating status of execution) and TransactionResult.
        """
        
        move_function_params = [
                    self.rfq_contracts.get_protocol_config(),
                    manager
                ]
        
        tx_bytes = rpc_unsafe_moveCall(
            url=self.url,
            params=move_function_params,
            function_name='create_rfq_vault',
            function_library='gateway',
            userAddress=self.wallet.getUserAddress(),
            packageId=self.rfq_contracts.get_package(),
            gasBudget=gasbudget
        )

        signature = self.signer.sign_tx(tx_bytes, self.wallet)
        res = rpc_sui_executeTransactionBlock(self.url, tx_bytes, signature)
        tx_response = TransactionResult(res)
        try:
            success = tx_response.effects.status == "success"
            return success, tx_response
        except Exception as e:
            return False , tx_response
    
    def deposit_in_vault(self, 
        vault: str,
        amount: str,
        coin_type: str,
        gasbudget: str | None = 100000000
        ) -> tuple[bool, TransactionResult] :
        """
        Deposits coin amount in the vault.

        Inputs:
          vault (str): on chain vault object ID.
          amount (str): amount of the coin that is to be deposited (scaled to supported coin decimals, eg. 1000000000 for 1 Sui).
          coin_type (str): on chain token type of input coin (i.e for USDC , usdc_Address::usdc::USDC).
          gasbudget (str, optional): Gas budget for transaction (default: "100000000", 0.1 Sui).

        Output:
          Tuple of bool (indicating status of execution) and TransactionResult.
        """

        coin_id = CoinUtils.create_coin_with_balance(
                coin_type=coin_type,
                balance=int(amount),
                wallet=self.wallet,
                url=self.url)
    
        move_function_params = [
                    vault,
                    self.rfq_contracts.get_protocol_config(),
                    coin_id
                ]
        move_function_type_arguments = [
                    coin_type
                ]
        
        tx_bytes = rpc_unsafe_moveCall(
            url=self.url,
            params=move_function_params,
            function_name='deposit',
            function_library='gateway',
            userAddress=self.wallet.getUserAddress(),
            packageId=self.rfq_contracts.get_package(),
            gasBudget=gasbudget,
            typeArguments=move_function_type_arguments
        )

        signature = self.signer.sign_tx(tx_bytes, self.wallet)
        res = rpc_sui_executeTransactionBlock(self.url, tx_bytes, signature)
        tx_response = TransactionResult(res)
        try:
            success = tx_response.effects.status == "success"
            return success, tx_response
        except Exception as e:
            return False , tx_response

    def withdraw_from_vault(self, 
        vault: str,
        amount: str,
        coin_type: str,
        gasbudget: str | None = 100000000
        ) -> tuple[bool, TransactionResult] :
        """
        Withdraws coin amount from the vault (Note: Only vault manager can withdraw from vault).

        Inputs:
          vault (str): on chain vault object ID.
          amount (str): amount of the coin that is to be withdrawn (scaled to supported coin decimals, eg. 1000000000 for 1 Sui).
          coin_type (str): on chain token type of the coin (i.e for USDC , usdc_Address::usdc::USDC).
          gasbudget (str, optional): Gas budget for transaction (default: "100000000", 0.1 Sui).

        Output:
          Tuple of bool (indicating status of execution) and TransactionResult.
        """    
        move_function_params = [
                    vault,
                    self.rfq_contracts.get_protocol_config(),
                    amount
                ]
        move_function_type_arguments = [
                    coin_type
                ]
        
        tx_bytes = rpc_unsafe_moveCall(
            url=self.url,
            params=move_function_params,
            function_name='withdraw',
            function_library='gateway',
            userAddress=self.wallet.getUserAddress(),
            packageId=self.rfq_contracts.get_package(),
            gasBudget=gasbudget,
            typeArguments=move_function_type_arguments
        )

        signature = self.signer.sign_tx(tx_bytes, self.wallet)
        res = rpc_sui_executeTransactionBlock(self.url, tx_bytes, signature)
        tx_response = TransactionResult(res)
        try:
            success = tx_response.effects.status == "success"
            return success, tx_response
        except Exception as e:
            return False , tx_response
        
    def update_vault_manager(self, 
        vault: str,
        new_manager: str,
        gasbudget: str | None = 100000000
        ) -> tuple[bool, TransactionResult] :
        """
        Updates the vault manager (Note: Only current manager can update vault manager).

        Inputs:
          vault (str): on chain vault object ID.
          new_manager (str): address of the new manager.
          gasbudget (str, optional): Gas budget for transaction (default: "100000000", 0.1 Sui).

        Output:
          Tuple of bool (indicating status of execution) and TransactionResult.
        """
        
        move_function_params = [
                    vault,
                    self.rfq_contracts.get_protocol_config(),
                    new_manager
                ]
        
        tx_bytes = rpc_unsafe_moveCall(
            url=self.url,
            params=move_function_params,
            function_name='set_manager',
            function_library='gateway',
            userAddress=self.wallet.getUserAddress(),
            packageId=self.rfq_contracts.get_package(),
            gasBudget=gasbudget
        )

        signature = self.signer.sign_tx(tx_bytes, self.wallet)
        res = rpc_sui_executeTransactionBlock(self.url, tx_bytes, signature)
        tx_response = TransactionResult(res)
        try:
            success = tx_response.effects.status == "success"
            return success, tx_response
        except Exception as e:
            return False , tx_response
        
    def update_min_deposit_for_coin(self, 
        vault: str,
        coin_type: str,
        min_amount: str,
        gasbudget: str | None = 100000000
        ) -> tuple[bool, TransactionResult] :
        """
        Updates minimum deposit amount for a coin (Note: Only vault manager can update min deposit).

        Inputs:
          vault (str): on chain vault object ID.
          coin_type (str): on chain token type of the coin (i.e for USDC , usdc_Address::usdc::USDC).
          min_amount (str): new minimum amount of the coin that can be deposited (scaled to supported coin decimals, eg. 1000000000 for 1 Sui).
          gasbudget (str, optional): Gas budget for transaction (default: "100000000", 0.1 Sui).

        Output:
          Tuple of bool (indicating status of execution) and TransactionResult.
        """
        
        move_function_params = [
                    vault,
                    self.rfq_contracts.get_protocol_config(),
                    min_amount
                ]
        move_function_type_arguments = [
                    coin_type
                ]
        
        tx_bytes = rpc_unsafe_moveCall(
            url=self.url,
            params=move_function_params,
            function_name='update_min_deposit',
            function_library='gateway',
            userAddress=self.wallet.getUserAddress(),
            packageId=self.rfq_contracts.get_package(),
            gasBudget=gasbudget,
            typeArguments=move_function_type_arguments
        )

        signature = self.signer.sign_tx(tx_bytes, self.wallet)
        res = rpc_sui_executeTransactionBlock(self.url, tx_bytes, signature)
        tx_response = TransactionResult(res)
        try:
            success = tx_response.effects.status == "success"
            return success, tx_response
        except Exception as e:
            return False , tx_response
    
    def add_coin_support(self, 
        vault: str,
        coin_type: str,
        min_amount: str,
        gasbudget: str | None = 100000000
        ) -> tuple[bool, TransactionResult] :
        """
        Adds support for a coin in the vault (Note: Only vault manager can add coin support).

        Inputs:
          vault (str): on chain vault object ID.
          coin_type (str): on chain token type of the coin (i.e for USDC , usdc_Address::usdc::USDC).
          min_amount (str): minimum amount of the coin that can be deposited (scaled to supported coin decimals, eg. 1000000000 for 1 Sui).
          gasbudget (str, optional): Gas budget for transaction (default: "100000000", 0.1 Sui).

        Output:
          Tuple of bool (indicating status of execution) and TransactionResult.
        """
        
        move_function_params = [
                    vault,
                    self.rfq_contracts.get_protocol_config(),
                    min_amount
                ]
        move_function_type_arguments = [
                    coin_type
                ]
        
        tx_bytes = rpc_unsafe_moveCall(
            url=self.url,
            params=move_function_params,
            function_name='support_coin',
            function_library='gateway',
            userAddress=self.wallet.getUserAddress(),
            packageId=self.rfq_contracts.get_package(),
            gasBudget=gasbudget,
            typeArguments=move_function_type_arguments
        )

        signature = self.signer.sign_tx(tx_bytes, self.wallet)
        res = rpc_sui_executeTransactionBlock(self.url, tx_bytes, signature)
        tx_response = TransactionResult(res)
        try:
            success = tx_response.effects.status == "success"
            return success, tx_response
        except Exception as e:
            return False , tx_response
        
    def get_vault_coin_balance(self, 
        vault: str,
        coin_type: str
        ) -> str :
        """
        Gets the balance of a specific coin in the vault.

        Inputs:
          vault (str): on chain vault object ID.
          coin_type (str): on chain token type of the coin (i.e for USDC , usdc_Address::usdc::USDC).

        Output:
          str: Balance of the coin (scaled to supported coin decimals, eg. 1000000000 for 1 Sui).
        """

        res = rpc_sui_getDynamicFieldObject(
            self.url,
            vault,
            strip_hex_prefix(coin_type),
            SUI_CUSTOM_OBJECT_TYPE)
        try:
            balance = res["result"]["data"]["content"]["fields"]["value"]["fields"]["swaps"]
            return balance
        except Exception as e:
            raise Exception(f"Failed to get vault coin balance, Exception: {e}")
        
        