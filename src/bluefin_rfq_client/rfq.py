from typing import Tuple
from .quote import Quote
from sui_utils import *
from .contracts import RFQContracts

class RFQClient:
    def __init__(self, wallet: SuiWallet = None , url: str = None, rfq_contracts : RFQContracts = None):
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

    @staticmethod
    def create_quote(
        vault: str,
        quote_id: str,
        taker: str,
        token_in_amount: int,
        token_out_amount: int,
        token_in_type: str,
        token_out_type: str,
        created_at_utc_sec: int = None,
        expires_at_utc_sec: int = None ) -> Quote:

        if created_at_utc_sec is None:
            created_at_utc_sec = int(datetime.now(timezone.utc).timestamp())
        if expires_at_utc_sec is None:
            expires_at_utc_sec = created_at_utc_sec + 10 # 10 seconds expiration

        return Quote(
            vault=vault,
            quote_id=quote_id,
            taker=taker,
            token_in_amount=token_in_amount,
            token_out_amount=token_out_amount,
            token_in_type=token_in_type,
            token_out_type=token_out_type,
            expires_at=expires_at_utc_sec,
            created_at=created_at_utc_sec,
        )

    def sign_quote(self, quote: Quote) -> str:
        bcs_serialized_bytes = Quote.get_bcs_serialized_quote(quote)

        # Sign bcs serialized quote bytes
        signature = self.wallet.sign_personal_msg(bcs_serialized_bytes)
    
        return signature.hex()
    
    def create_and_sign_quote(
        self, 
        vault: str,
        quote_id: str,
        taker: str,
        token_in_amount: int,
        token_out_amount: int,
        token_in_type: str,
        token_out_type: str,
        created_at_utc_sec: int = None,
        expires_at_utc_sec: int = None ) -> Tuple[Quote,str]:

        if created_at_utc_sec is None:
            created_at_utc_sec = int(datetime.now(timezone.utc).timestamp())
        if expires_at_utc_sec is None:
            expires_at_utc_sec = created_at_utc_sec + 10 # 10 seconds expiration

        quote = Quote(
            vault=vault,
            id=quote_id,
            taker=taker,
            token_in_amount=token_in_amount,
            token_out_amount=token_out_amount,
            token_in_type=token_in_type,
            token_out_type=token_out_type,
            expires_at=expires_at_utc_sec,
            created_at=created_at_utc_sec,
        )

        bcs_serialized_bytes = Quote.get_bcs_serialized_quote(quote)

        # Sign bcs serialized quote bytes
        signature = self.wallet.sign_personal_msg(bcs_serialized_bytes)
    
        return (quote, signature.hex())
    
    def deposit_in_vault(self, 
        vault: str,
        amount: str,
        token_type: str
        ) -> tuple[bool, dict] :
        

        coin_id = get_coin_having_balance(
            user_address=self.wallet.getUserAddress(),
            coin_type=token_type,
            balance=amount,
            url=self.url,
            exact_match=True)
    
        move_function_params = [
                    vault,
                    self.rfq_contracts.get_protocol_config(),
                    coin_id
                ]
        move_function_type_arguments = [
                    token_type
                ]
        
        tx_bytes = rpc_unsafe_moveCall(
            url=self.url,
            params=move_function_params,
            function_name='deposit',
            function_library='gateway',
            userAddress=self.wallet.getUserAddress(),
            packageId=self.rfq_contracts.get_package(),
            gasBudget=1000000000,
            typeArguments=move_function_type_arguments
        )

        signature = self.signer.sign_tx(tx_bytes, self.wallet)
        res = rpc_sui_executeTransactionBlock(self.url, tx_bytes, signature)
        try:
            success = res["result"]["effects"]["status"]["status"] == "success"
            return success, res
        except Exception as e:
            return False , res

    def withdraw_from_vault(self, 
        vault: str,
        amount: str,
        token_type: str
        ) -> tuple[bool, dict] :
        

    
        move_function_params = [
                    vault,
                    self.rfq_contracts.get_protocol_config(),
                    amount
                ]
        move_function_type_arguments = [
                    token_type
                ]
        
        tx_bytes = rpc_unsafe_moveCall(
            url=self.url,
            params=move_function_params,
            function_name='withdraw',
            function_library='gateway',
            userAddress=self.wallet.getUserAddress(),
            packageId=self.rfq_contracts.get_package(),
            gasBudget=1000000000,
            typeArguments=move_function_type_arguments
        )

        signature = self.signer.sign_tx(tx_bytes, self.wallet)
        res = rpc_sui_executeTransactionBlock(self.url, tx_bytes, signature)
        try:
            success = res["result"]["effects"]["status"]["status"] == "success"
            return success, res
        except Exception as e:
            return False , res
        