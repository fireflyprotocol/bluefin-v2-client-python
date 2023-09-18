from pprint import pprint
import asyncio
from config import TEST_ACCT_KEY, TEST_NETWORK
from bluefin_v2_client import BluefinClient, Networks, MARKET_SYMBOLS


async def main():
    client = BluefinClient(
        True,  # agree to terms and conditions
        Networks[TEST_NETWORK],  # network to connect with
        TEST_ACCT_KEY,  # seed phrase of the wallet
    )

    # initialize the client
    # on boards user on Bluefin. Must be set to true for first time use
    await client.init(True)

    # gets user account data on Bluefin exchange
    data = await client.get_user_account_data()
    pprint(data)

    position = await client.get_user_position({"symbol": MARKET_SYMBOLS.ETH})
    pprint(position)  # returns {} when user has no position

    position = await client.get_user_position({"symbol": MARKET_SYMBOLS.BTC})
    pprint(position)  # returns user position if exists

    await client.close_connections()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    loop.close()
