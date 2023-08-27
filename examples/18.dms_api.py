import json

import sys, os

sys.path.append(os.getcwd() + "/src/")
from config import TEST_ACCT_KEY, TEST_SUB_ACCT_KEY, TEST_NETWORK
from bluefin_client_sui import (
    BluefinClient,
    MARKET_SYMBOLS,
    ORDER_SIDE,
    ORDER_TYPE,
    Networks,
    OrderSignatureRequest,
)
import asyncio

from bluefin_client_sui.interfaces import PostTimerAttributes


async def main():
    client = BluefinClient(True, Networks[TEST_NETWORK], TEST_ACCT_KEY)
    await client.init(True)

    print("User: ", client.get_public_address())
    countDownsObject: PostTimerAttributes = dict()
    countDowns = list()
    countDowns.append({"symbol": MARKET_SYMBOLS.BTC.value, "countDown": 3 * 1000})

    countDowns.append({"symbol": MARKET_SYMBOLS.ETH.value, "countDown": 3 * 1000})

    countDownsObject["countDowns"] = countDowns
    try:
        # sending post request to reset user's count down timer with MARKET_SYMBOL for auto cancellation of order
        postResponse = await client.reset_cancel_on_disconnect_timer(countDownsObject)
        print(postResponse)
        # get request to get user's count down timer for MARKET_SYMBOL
        getResponse = await client.get_cancel_on_disconnect_timer(
            {"symbol": MARKET_SYMBOLS.ETH}
        )
        print(getResponse)

    except Exception as e:
        print(e)

    await client.close_connections()


if __name__ == "__main__":
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(main())
