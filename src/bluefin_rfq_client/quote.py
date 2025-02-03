
from sui_utils.bcs import BCSSerializer
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
        """
        Initialize the Quote instance with provided input fields.

        Parameters:
        vault (str): on chain vault object ID.
        id (int): unique quote ID assigned for on chain verification and security.
        taker (str): address of the reciever account.
        token_in_amount (int): amount of the input token reciever is willing to swap [scaled to default base of the coin (i.e for 1 USDC(1e6) , provide input as 1000000 )]
        token_out_amount (int): amount of the output token to be paid by quote initiator [scaled to default base of the coin (i.e for 1 SUI(1e9) , provide input as 1000000000 )]
        token_in_type (str): on chain token type of input coin (i.e for SUI , 0x2::sui::SUI)
        token_out_type (str): on chain token type of output coin (i.e for USDC , usdc_Address::usdc::USDC)
        created_at (int): the unix timestamp at which the quote was created in milliseconds
        expires_at (int): the unix timestamp at which the quote is to be expired in milliseconds

        Returns:
        instance of Quote
        """
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
        """
        Returns BCS serialized bytes of the quote.

        :param quote (Quote): instance of Quote class.

        Returns:
        bytes
        """
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

