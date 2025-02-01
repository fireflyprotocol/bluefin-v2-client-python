
from sui_utils import BCSSerializer
from typing import Self


# Defines the Quote class
class Quote:
    def __init__(
        self,
        vault: str,
        id: str,
        taker: str,
        token_in_amount: int,
        token_out_amount: int,
        token_in_type: str,
        token_out_type: str,
        created_at: int = None,
        expires_at: int = None
    ):
        self.vault = vault
        self.id = id
        self.taker = taker
        self.token_in_amount = token_in_amount
        self.token_out_amount = token_out_amount
        self.token_in_type = token_in_type
        self.token_out_type = token_out_type
        self.expires_at = expires_at
        self.created_at = created_at

    @staticmethod
    def get_bcs_serialized_quote(quote: Self) -> bytes:
        serializer = BCSSerializer()

        # Apply BCS serialization to the Quote in correct order
        serializer.serialize_address(quote.vault)  
        serializer.serialize_str(quote.id) 
        serializer.serialize_address(quote.taker)  
        serializer.serialize_u64(quote.token_in_amount) 
        serializer.serialize_u64(quote.token_out_amount)  
        serializer.serialize_str(quote.token_in_type) 
        serializer.serialize_str(quote.token_out_type)  
        serializer.serialize_u64(quote.expires_at)  
        serializer.serialize_u64(quote.created_at)  

        return serializer.get_bytes()

