import nacl
import hashlib
import json
import base64
from nacl.signing import *
from .enumerations import WALLET_SCHEME
from .account import SuiWallet
from .utilities import *
from .bcs import *


class Signer:
    def __init__(self):
        pass

    def sign_tx(self, tx_bytes_str: str, sui_wallet: SuiWallet) -> str:
        """
        expects the msg in str
        expects the suiwallet object
        Signs the msg and returns the signature.
        Returns the value in b64 encoded format
        """
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

    def sign_hash(self, hash, private_key, append=""):
        """
        Signs the hash and returns the signature.
        """
        result = nacl.signing.SigningKey(private_key).sign(hash)[:64]
        return result.hex() + "1" + append

    def encode_message(self, msg: dict):
        msg = json.dumps(msg, separators=(",", ":"))
        msg_bytearray = bytearray(msg.encode("utf-8"))
        intent = bytearray()
        encodeLengthBCS = decimal_to_bcs(len(msg_bytearray))
        intent.extend([3, 0, 0])
        intent.extend(encodeLengthBCS)
        intent = intent + msg_bytearray
        hash = hashlib.blake2b(intent, digest_size=32)
        return hash.digest()
    
    def sign_personal_msg(self, serialized_bytes: bytearray, wallet : SuiWallet ):
        serializer = BCSSerializer()
        # this function adds len as an Unsigned Little Endian Base 128 similar to mysten SDK
        serializer.serialize_uint8_array(list(serialized_bytes))
        serialized_bytes = serializer.get_bytes()

        # Add personal message intent bytes
        intent = bytearray()
        intent.extend([ 3, 0, 0]) # Intent scope for personal message

        # Combine the intent and msg_bytes
        intent = intent + serialized_bytes

        # Combine blake2b hash
        blake2bHash = hashlib.blake2b(intent, digest_size=32).digest()

        # Sign the hash
        signature = nacl.signing.SigningKey(wallet.privateKeyBytes).sign(blake2bHash)[:64]


        serializer = BCSSerializer()
        serializer.serialize_u8(WALLET_SCHEME[wallet.getKeyScheme()])
        
        # Construct Signature in accurate format (scheme + signature + publicKey)
        return serializer.get_bytes()+ signature + wallet.publicKeyBytes
    
    def sign_bytes(self, bytes: bytearray, private_key: bytes) -> bytes:
        """
        Signs the bytes and returns the signature bytes.
        """
        result = nacl.signing.SigningKey(private_key).sign(bytes)[:64]
        return result

    def verify_signature(self, message: bytes, signature: bytes, public_key: bytes, scheme: str) -> bool:
        """
        Verifies the signature using the specified scheme.

        Parameters:
        message (bytes): The message to verify.
        signature (bytes): The signature to verify.
        public_key (bytes): The public key to use for verification.
        scheme (str): The signature scheme.

        Returns:
        bool: True if the signature is valid, False otherwise.
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

        Parameters:
        signature (bytes): The serialized signature.

        Returns:
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

    


    