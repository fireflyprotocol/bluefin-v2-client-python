import sys, os

sys.path.append(os.getcwd() + "/src/")
import base64
from bluefin_v2_client.utilities import *
from config import TEST_ACCT_KEY, TEST_NETWORK
from bluefin_v2_client import (
    BluefinClient,
    Networks,
    MARKET_SYMBOLS,
    ORDER_SIDE,
    ORDER_TYPE,
    OrderSignatureRequest,
)
import asyncio
from bluefin_v2_client import signer
from bluefin_v2_client import *


async def main():
    # initialize client
    client = BluefinClient(
        True,  # agree to terms and conditions
        Networks[TEST_NETWORK],  # network to connect with
        TEST_ACCT_KEY,  # seed phrase of the wallet
    )
    await client.init(True)

    await client.withdraw_margin_from_bank(1000)

    txBytes = "AAADAQGPzuAZV5krLKJWD1WUXOjk7Guz2vki2pBMZJ6CXkRf1XLGgQAAAAAAAQAgH/qFdX+Vzs7ShiLTDkGkUsiFFt9TRQyxkTgS3YKNWWgAEOgDAAAAAAAAAAAAAAAAAAABAF82iNaL7Cly31h0P767ErFoKbQb8bxQeNNRAJDvbPWOC21hcmdpbl9iYW5rEndpdGhkcmF3X2Zyb21fYmFuawADAQAAAQEAAQIAH/qFdX+Vzs7ShiLTDkGkUsiFFt9TRQyxkTgS3YKNWWgBWiybg/9fRf7zXUmsdBU3umIFeucEZNWeMGzlLttPf86tHg8AAAAAACA3qZfzxP1+yVILtVkJ6LdfZvkF7gK877AJco9Xook9Th/6hXV/lc7O0oYi0w5BpFLIhRbfU0UMsZE4Et2CjVlo6AMAAAAAAAAA4fUFAAAAAAA="
    dec_msg = base64.b64decode(txBytes)
    mysigner = signer.Signer()

    seed = "negative repeat fold noodle symptom spirit spend trophy merge ethics math erupt"
    sui_wallet = SuiWallet(seed=seed)

    result = mysigner.sign_tx(dec_msg, sui_wallet)
    print(result)

    await client.close_connections()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    loop.close()
