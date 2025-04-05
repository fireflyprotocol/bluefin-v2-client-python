import nacl
import hashlib
import json
import base64
from nacl.signing import *
from .sui_interfaces import TransactionResult
from .enumerations import WALLET_SCHEME
from .account import SuiWallet
from .utilities import *
from .bcs import *
from .rpc import rpc_sui_executeTransactionBlock


class Signer:
    """
    A class to sign transactions and execute them on the SUI chain.
    """
    def __init__(self, sui_wallet: SuiWallet = None):
        """
        Initializes the Signer class.
        Input:
            sui_wallet: optional SuiWallet object.
        """
        self.sui_wallet = sui_wallet
    
    def sign_tx(self, tx_bytes_str: str, sui_wallet: SuiWallet = None) -> str:
        """
        Signs the transaction and returns the signature.
        Input:
            tx_bytes_str: The transaction bytes in base64 encoded string format.
            sui_wallet: optional SuiWallet object.
        Output:
            Returns the signature in base64 encoded format.
        """
        
        # pick sui wallet from fucntion parameter or from the class instance
        preferred_sui_wallet = sui_wallet

        # if no sui wallet is provided, use the one from the class instance
        if preferred_sui_wallet is None:
            preferred_sui_wallet = self.sui_wallet

        # if no sui wallet is provided, nor from the class instance, raise an error
        if preferred_sui_wallet is None:
            raise ValueError("SuiWallet is not provided")

        tx_bytes = base64.b64decode(tx_bytes_str)

        intent = bytearray()
        intent.extend([0, 0, 0])
        intent = intent + tx_bytes
        hash = hashlib.blake2b(intent, digest_size=32).digest()

        result = nacl.signing.SigningKey(sui_wallet.privateKeyBytes).sign(hash)[:64]
        temp = bytearray()
        temp.append(0)
        temp.extend(result)
        temp.extend(sui_wallet.publicKeyBytes)
        res = base64.b64encode(temp)
        return res.decode()
    
  
    def sign_and_execute_tx(self, tx_bytes: str, sui_wallet: SuiWallet = None, url: str = None) -> TransactionResult:
        """
        Signs the transaction and executes it on the SUI chain.
        
        Input:
            tx_bytes (str): The transaction bytes in string format.
            sui_wallet (SuiWallet): The SuiWallet object.
            url (str): The URL of the node.

        Output:
            dict: The result of the transaction execution.
        """
        
        # pick sui wallet from fucntion parameter or from the class instance
        preferred_sui_wallet = sui_wallet

        # if no sui wallet is provided, use the one from the class instance
        if preferred_sui_wallet is None:
            preferred_sui_wallet = self.sui_wallet

        # if no sui wallet is provided, nor from the class instance, raise an error
        if preferred_sui_wallet is None:
            raise ValueError("SuiWallet is not provided")
        
        try:
            signature = self.sign_tx(tx_bytes, preferred_sui_wallet)
            tx = rpc_sui_executeTransactionBlock(url, tx_bytes, signature)
            return TransactionResult(tx)
        except Exception as e:
            raise Exception(f"Failed to sign and execute transaction, Exception: {e}")

    
    def sign_hash(self, hash, private_key, append=""):
        """
        Signs the hash and returns the signature.
        Input:
            hash: The hash to sign.
            private_key: The private key to sign the hash.
            append: optional string to append to the signature.
        Output:
            Returns the signature of the hash in bytes format.
        """
        result = nacl.signing.SigningKey(private_key).sign(hash)[:64]
        return result.hex() + "1" + append

    
    def encode_message(self, msg: dict) -> bytes:
        """
        Encodes the message and returns the hash.
        Input:
            msg: The message to encode.
        Output:
            Returns the hash of the message in bytes format.
        """
        msg = json.dumps(msg, separators=(",", ":"))
        msg_bytearray = bytearray(msg.encode("utf-8"))
        intent = bytearray()
        encodeLengthBCS = decimal_to_bcs(len(msg_bytearray))
        intent.extend([3, 0, 0])
        intent.extend(encodeLengthBCS)
        intent = intent + msg_bytearray
        hash = hashlib.blake2b(intent, digest_size=32)
        return hash.digest()
    
    def sign_personal_msg(self, serialized_bytes: bytearray, wallet: SuiWallet = None) -> bytes:
        """
        Signs the personal message and returns the signature.
        Input:
            serialized_bytes: The serialized bytes of the message.
            wallet: The wallet to sign the message.
        Output:
            Returns the signature of the message in bytes format.
        """
        # pick wallet from fucntion parameter or from the class instance
        preferred_wallet = wallet

        # if no wallet is provided, use the one from the class instance
        if preferred_wallet is None:
            preferred_wallet = self.sui_wallet

        # if no wallet is provided, nor from the class instance, raise an error
        if preferred_wallet is None:
            raise ValueError("SuiWallet is not provided")

        serializer = BCSSerializer()
        # this function adds len as an Unsigned Little Endian Base 128 similar to mysten SDK
        serializer.serialize_uint8_array(list(serialized_bytes))
        serialized_bytes = serializer.get_bytes()

        # Add personal message intent bytes
        intent = bytearray()
        intent.extend([3, 0, 0]) # Intent scope for personal message

        # Combine the intent and msg_bytes
        intent = intent + serialized_bytes

        # Combine blake2b hash
        blake2bHash = hashlib.blake2b(intent, digest_size=32).digest()

        # Sign the hash
        signature = nacl.signing.SigningKey(wallet.privateKeyBytes).sign(blake2bHash)[:64]

        serializer = BCSSerializer()
        serializer.serialize_u8(WALLET_SCHEME[wallet.getKeyScheme()])
        
        # Construct Signature in accurate format (scheme + signature + publicKey)
        return serializer.get_bytes() + signature + wallet.publicKeyBytes
    
    def sign_bytes(self, bytes: bytearray, private_key: bytes = None) -> bytes:
        """
        Signs the provided bytes and returns the signature.
        Input:
            bytes: The bytes to sign.
            private_key: The private key to sign the bytes.
        Output:
            Returns the signature of the bytes in bytes format.
        """
        # if no private key is provided, use the one from the class instance
        preferred_private_key = private_key

        # if no private key is provided, use the one from the class instance
        if preferred_private_key is None:
            preferred_private_key = self.sui_wallet.privateKeyBytes

        # if no private key is provided, nor from the class instance, raise an error    
        if preferred_private_key is None:
            raise ValueError("Private key is not provided")

        result = nacl.signing.SigningKey(preferred_private_key).sign(bytes)[:64]
        return result

    def verify_signature(self, message: bytes, signature: bytes, public_key: bytes, scheme: str) -> bool:
        """
        Verifies the signature using the specified scheme.
        Input:
            message (bytes): The message to verify.
            signature (bytes): The signature to verify.
            public_key (bytes): The public key to use for verification.
            scheme (str): The signature scheme.

        Output:
            Returns True if the signature is valid, False otherwise.
        """
        if scheme == "ED25519":
            verify_key = VerifyKey(public_key)
            try:
                verify_key.verify(message, signature)
                return True
            except Exception:
                print("Exception")
                return False
        else:
            raise ValueError("Invalid signature scheme")
        
    def parse_serialized_signature(self, signature: bytes) -> dict:
        """
        Parses the serialized signature to extract the scheme, signature, and public key.

        Input:
            signature (bytes): The serialized signature.

        Output:
            dict: A dictionary containing the signature scheme, signature, and public key.
        """
        scheme = signature[0]
        signature_bytes = signature[1:65]
        public_key = signature[65:]

        if scheme == 0:
            signature_scheme = "ED25519"
        else:
            raise ValueError("Invalid signature scheme")

        return {
            "signatureScheme": signature_scheme,
            "signature": signature_bytes,
            "publicKey": public_key
        }




