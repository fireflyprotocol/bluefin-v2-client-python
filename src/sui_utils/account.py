import nacl
import nacl.signing
from .utilities import *
import base64
from .bcs import *


class SuiWallet:
    def __init__(self, seed="", privateKey=""):
        if seed == "" and privateKey == "":
            return "Error"
        if seed != "":
            self.privateKey = mnemonicToPrivateKey(seed)
            self.publicKey = privateKeyToPublicKey(self.privateKey)
            self.key = self.getPrivateKey()
            self.publicKeyBase64 = base64.b64encode(self.publicKey.ToBytes()[1:])
            self.privateKeyBase64 = base64.b64encode(self.privateKey.ToBytes()[1:])
            self.privateKeyBytes = self.privateKey.ToBytes()

        elif privateKey != "":
            self.privateKey = privateKey
            self.publicKey = privateKeyToPublicKey(self.privateKey)
            self.key = self.getPrivateKey()
            self.publicKeyBase64 = base64.b64encode(self.publicKey.ToBytes()[1:])
            self.privateKeyBase64 = base64.b64encode(binascii.unhexlify(self.privateKey)[1:])
            self.privateKeyBytes = binascii.unhexlify(self.privateKey)

        else:
            return "error"
            

        self.publicKeyBytes = self.publicKey.ToBytes()
        self.address = getAddressFromPublicKey(self.publicKey)

    def getPublicKey(self):
        if type(self.publicKey) is str:
            return self.publicKey
        else:
            return self.publicKey.ToHex()

    def getPrivateKey(self):
        if type(self.privateKey) is str:
             return self.privateKey
        else:
             return self.privateKey.ToHex()


    def getUserAddress(self):
        return self.address
    
    def sign_personal_msg(self, serialized_bytes: bytearray):
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
        signature = nacl.signing.SigningKey(self.privateKeyBytes).sign(blake2bHash)[:64]

        
        ED25519_SCHEME_FLAG = 0
        serializer = BCSSerializer()
        serializer.serialize_u8(ED25519_SCHEME_FLAG)
        
        # Construct Signature in accurate format (scheme + signature + publicKey)
        return serializer.get_bytes()+ signature + self.publicKeyBytes[1:]
