import sys, os

sys.path.append(os.getcwd() + "/src/")
from config import TEST_ACCT_KEY, TEST_NETWORK
from bluefin_client_sui import BluefinClient, Networks, MARKET_SYMBOLS
from pprint import pprint
import asyncio


async def main():
    # create client instance
    client = BluefinClient(
        True,  # agree to terms and conditions
        Networks[TEST_NETWORK],  # network to connect with
        TEST_ACCT_KEY,  # private key of wallet
    )

    # initialize the client
    # on boards user on Bluefin. Must be set to true for first time use
    await client.init(True)

    # gets user account data on Bluefin exchange
    data = await client.get_user_account_data()

    pprint(data)

    position = await client.get_user_position({"symbol": MARKET_SYMBOLS.ETH})

    # returns {} when user has no position
    pprint(position)

    position = await client.get_user_position({"symbol": MARKET_SYMBOLS.BTC})

    # returns user position if exists
    pprint(position)

    await client.close_connections()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    loop.close()
