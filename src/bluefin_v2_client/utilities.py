from datetime import datetime
from random import randint

# from web3 import Web3
import time
from typing import Union
import bip_utils
import hashlib


BASE_1E18 = 1000000000000000000
BASE_1E6 = 1000000  # 1e6 for USDC token
BASE_1E9 = 1000000000


def to1e18(number: Union[int, float]) -> int:
    """Takes in a number and multiples it by 1e18"""
    return int(number * BASE_1E18)


def from1e18(number: Union[str, int]) -> float:
    """Takes in a number and divides it by 1e18"""
    number = float(number)
    return number / float(BASE_1E18)


def fromSuiBase(number: Union[str, int]) -> float:
    """Takes in a number and divides it by 1e9"""
    number = float(number)
    return number / float(BASE_1E9)


def toSuiBase(number: Union[str, int]) -> int:
    """Takes in a number and multiplies it by 1e9"""
    number = int(number)
    return number * BASE_1E9


def toUsdcBase(number: Union[int, float]) -> int:
    """Converts a number to usdc contract onchain representation i.e. multiply it by 1e6"""
    return int(number * BASE_1E6)


def fromUsdcBase(number: Union[str, int]) -> float:
    """Converts a usdc quantity to number i.e. divide it by 1e6"""
    number = float(number)
    return number / float(BASE_1E6)


def numberToHex(num, pad=32):
    hexNum = hex(num)
    # padding it with zero to make the size 32 bytes
    padHex = hexNum[2:].zfill(pad)
    return padHex


def hexToByteArray(hexStr):
    return bytearray.fromhex(hexStr)


def mnemonicToPrivateKey(seedPhrase: str) -> str:
    bip39_seed = bip_utils.Bip39SeedGenerator(seedPhrase).Generate()
    bip32_ctx = bip_utils.Bip32Slip10Ed25519.FromSeed(bip39_seed)
    derivation_path = "m/44'/784'/0'/0'/0'"
    bip32_der_ctx = bip32_ctx.DerivePath(derivation_path)
    private_key: str = bip32_der_ctx.PrivateKey().Raw()
    return private_key


def privateKeyToPublicKey(privateKey: str) -> str:
    privateKeyBytes = bytes(privateKey)
    bip32_ctx = bip_utils.Bip32Slip10Ed25519.FromPrivateKey(privateKeyBytes)
    public_key: str = bip32_ctx.PublicKey().RawCompressed()
    return public_key


def getAddressFromPublicKey(publicKey: str) -> str:
    address: str = (
        "0x" + hashlib.blake2b(publicKey.ToBytes(), digest_size=32).digest().hex()[:]
    )
    return address


def strip_hex_prefix(input):
    if input[0:2] == "0x":
        return input[2:]
    else:
        return input


def address_to_bytes32(addr):
    return "0x000000000000000000000000" + strip_hex_prefix(addr)


def bn_to_bytes8(value: int):
    return str("0x" + "0" * 16 + hex(value)[2:]).encode("utf-8")


def default_value(dict, key, default_value):
    if key in dict:
        return dict[key]
    else:
        return default_value


def default_enum_value(dict, key, default_value):
    if key in dict:
        return dict[key].value
    else:
        return default_value.value


def current_unix_timestamp():
    return int(datetime.now().timestamp())


def random_number(max_range):
    return current_unix_timestamp() + randint(0, max_range) + randint(0, max_range)


def extract_query(value: dict):
    query = ""
    for i, j in value.items():
        query += "&{}={}".format(i, j)
    return query[1:]


def extract_enums(params: dict, enums: list):
    for i in enums:
        if i in params.keys():
            if type(params[i]) == list:
                params[i] = [x.value for x in params[i]]
            else:
                params[i] = params[i].value
    return params


def config_logging(logging, logging_level, log_file: str = None):
    """Configures logging to provide a more detailed log format, which includes date time in UTC
    Example: 2021-11-02 19:42:04.849 UTC <logging_level> <log_name>: <log_message>
    Args:
        logging: python logging
        logging_level (int/str): For logging to include all messages with log levels >= logging_level. Ex: 10 or "DEBUG"
                                 logging level should be based on https://docs.python.org/3/library/logging.html#logging-levels
    Keyword Args:
        log_file (str, optional): The filename to pass the logging to a file, instead of using console. Default filemode: "a"
    """

    logging.Formatter.converter = time.gmtime  # date time in GMT/UTC
    logging.basicConfig(
        level=logging_level,
        filename=log_file,
        format="%(asctime)s.%(msecs)03d UTC %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
