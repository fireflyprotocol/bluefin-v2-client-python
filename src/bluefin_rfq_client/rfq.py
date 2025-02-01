from typing import Tuple
from quote import Quote
from sui_utils import *

class RFQClient:
    def __init__(self, wallet: SuiWallet):
        if wallet is None:
            raise ValueError(
                "Initialize SuiWallet to use RFQClient")
        self.wallet = wallet

    def create_quote(
        self, 
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
            quote_id=quote_id,
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