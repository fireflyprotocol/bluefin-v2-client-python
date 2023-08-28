from .utilities import *
import base64


class SuiWallet:
    def __init__(self, seed="", privateKey=""):
        if seed == "" and privateKey == "":
            return "Error"
        if seed != "":
            self.privateKey = mnemonicToPrivateKey(seed)
            self.publicKey = privateKeyToPublicKey(self.privateKey)
            self.key = self.getPrivateKey()
        elif privateKey != "":
            self.privateKey = privateKey
            self.publicKey = privateKeyToPublicKey(self.privateKey)
            self.key = self.getPrivateKey()

        else:
            return "error"

        self.publicKeyBase64 = base64.b64encode(self.publicKey.ToBytes()[1:])
        self.privateKeyBase64 = base64.b64encode(self.privateKey.ToBytes()[1:])

        self.privateKeyBytes = self.privateKey.ToBytes()
        self.publicKeyBytes = self.publicKey.ToBytes()

        self.address = getAddressFromPublicKey(self.publicKey)

    def getPublicKey(self):
        return self.publicKey.ToHex()

    def getPrivateKey(self):
        return self.privateKey.ToHex()

    def getUserAddress(self):
        return self.address
