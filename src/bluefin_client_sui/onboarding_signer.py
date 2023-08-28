from .interfaces import *
from .signer import Signer
import hashlib
import json


class OnboardingSigner(Signer):
    def __init__(self):
        super().__init__()

    def create_signature(self, msg, private_key, encoding="utf-8"):
        """
        Signs the message.
        Inputs:
            - msg: the message to be signed
            - private_key: the signer's private key
        Returns:
            - str: signed msg hash
        """
        msgDict = {}
        msgDict["onboardingUrl"] = msg
        msg = json.dumps(msgDict, separators=(",", ":"))
        msg_bytearray = bytearray(msg.encode("utf-8"))
        intent = bytearray()
        intent.extend([3, 0, 0, len(msg_bytearray)])
        intent = intent + msg_bytearray

        hash = hashlib.blake2b(intent, digest_size=32)
        return self.sign_hash(hash.digest(), private_key)
