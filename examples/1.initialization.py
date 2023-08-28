import os
import sys

print(os.getcwd())
sys.path.append(os.getcwd() + "/src/")

from config import TEST_ACCT_KEY, TEST_NETWORK

from bluefin_client_sui import BluefinClient, Networks
from pprint import pprint
import asyncio


async def main():
    # initialize client
    client = BluefinClient(
        True,  # agree to terms and conditions
        Networks[TEST_NETWORK],  # network to connect with
        TEST_ACCT_KEY,  # private key of wallet
    )

    # Initializing client for the private key provided. The second argument api_token is optional
    await client.init(True)

    print("Account Address:", client.get_public_address())

    # # gets user account data on-chain
    data = await client.get_user_account_data()

    await client.close_connections()

    pprint(data)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    loop.close()
