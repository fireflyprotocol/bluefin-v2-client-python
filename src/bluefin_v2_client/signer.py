import nacl
import hashlib
import json
import base64
from .utilities import *
from .account import *


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
        temp.extend(sui_wallet.publicKeyBytes[1:])
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
        encodeLengthBCS = self.decimal_to_bcs(len(msg_bytearray))
        intent.extend([3, 0, 0])
        intent.extend(encodeLengthBCS)
        intent = intent + msg_bytearray
        hash = hashlib.blake2b(intent, digest_size=32)
        return hash.digest()

    def decimal_to_bcs(self, num):
        # Initialize an empty list to store the BCS bytes
        bcs_bytes = []
        while num > 0:
            # Take the last 7 bits of the number
            bcs_byte = num & 0x7F

            # Set the most significant bit (MSB) to 1 if there are more bytes to follow
            if num > 0x7F:
                bcs_byte |= 0x80

            # Append the BCS byte to the list
            bcs_bytes.append(bcs_byte)

            # Right-shift the number by 7 bits to process the next portion
            num >>= 7

        return bcs_bytes
