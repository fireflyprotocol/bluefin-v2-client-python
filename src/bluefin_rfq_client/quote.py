
from sui_utils import *


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
        self.signer = Signer()

    def get_bcs_serialized_quote(self) -> bytes:
        """
        Returns BCS serialized bytes of the quote.

        :param quote (Quote): instance of Quote class.

        Returns:
        bytes
        """
        serializer = BCSSerializer()

        # Apply BCS serialization to the Quote in correct order
        serializer.serialize_address(self.vault)  
        serializer.serialize_str(self.id) 
        serializer.serialize_address(self.taker)  
        serializer.serialize_u64(self.token_in_amount) 
        serializer.serialize_u64(self.token_out_amount)  
        serializer.serialize_str(self.token_in_type) 
        serializer.serialize_str(self.token_out_type)  
        serializer.serialize_u64(self.expires_at)  
        serializer.serialize_u64(self.created_at)  

        return serializer.get_bytes()
    
    def sign(self, wallet: SuiWallet) -> bytes:
        serializedBytes = self.get_bcs_serialized_quote()
        signature = self.signer.sign_bytes(serializedBytes,wallet.privateKeyBytes)
        scheme = wallet.getKeyScheme()

        signatureBytes = bytearray()
        if scheme == WALLET_SCHEME.ED25519:
            signatureBytes.append(0)
        else:
            signatureBytes.append(1)
        
        signatureBytes.extend(signature)
        signatureBytes.extend(wallet.publicKeyBytes)

        return signatureBytes

    def verify_signature(self, signature_hex: str, signer: str) -> bool:
        try:
            signature_bytes = bytes.fromhex(signature_hex)
            parsed = self.signer.parse_serialized_signature(signature_bytes)
            verified = self.signer.verify_signature(
                self.get_bcs_serialized_quote(),
                parsed['signature'],
                parsed['publicKey'],
                parsed['signatureScheme']
            )

            if not verified:
                return False
            
            address = getAddressFromPublicKey(f"00{parsed['publicKey'].hex()}")

            return address == signer
        except Exception as e:
            return False


