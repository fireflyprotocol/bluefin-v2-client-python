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
            print(self.getPublicKey())
            self.key = self.getPrivateKey()

        else:
            return "error"

        self.publicKeyBase64 = base64.b64encode(self.publicKey.ToBytes()[1:])
        self.privateKeyBase64 = base64.b64encode(bytes.fromhex(self.privateKey)[1:])

        self.privateKeyBytes = bytes.fromhex(self.privateKey)
        self.publicKeyBytes = self.publicKey.ToBytes()

        self.address = getAddressFromPublicKey(self.publicKey)

    def getPublicKey(self):
        return self.publicKey

    def getPrivateKey(self):
        return self.privateKey

    def getUserAddress(self):
        return self.address
