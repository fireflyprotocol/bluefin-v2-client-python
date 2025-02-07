from .enumerations import WALLET_SCHEME
from .utilities import *
import base64
from .bcs import *


class SuiWallet:
    def __init__(self, seed="", privateKey="",scheme:WALLET_SCHEME = WALLET_SCHEME.ED25519):
        if seed == "" and privateKey == "":
            return "Error"
        if seed != "":
            self.privateKey = mnemonicToPrivateKey(seed)
            self.publicKey = privateKeyToPublicKey(self.privateKey)
            self.key = self.getPrivateKey()
            self.publicKeyBase64 = base64.b64encode(self.publicKey.ToBytes()[1:])
            self.privateKeyBase64 = base64.b64encode(self.privateKey.ToBytes()[1:])
            self.privateKeyBytes = self.privateKey.ToBytes()
            self.scheme = scheme

        elif privateKey != "":
            self.privateKey = privateKey
            self.publicKey = privateKeyToPublicKey(self.privateKey)
            self.key = self.getPrivateKey()
            self.publicKeyBase64 = base64.b64encode(self.publicKey.ToBytes()[1:])
            self.privateKeyBase64 = base64.b64encode(binascii.unhexlify(self.privateKey)[1:])
            self.privateKeyBytes = binascii.unhexlify(self.privateKey)
            self.scheme = scheme

        else:
            return "error"
            

        self.publicKeyBytes = self.publicKey.ToBytes()[1:]
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
    
    def getKeyScheme(self):
        return self.scheme
    
    