from config import TEST_ACCT_KEY, TEST_NETWORK
from pprint import pprint
import asyncio

from bluefin_v2_client import BluefinClient, Networks


async def main():
    # initialize client
    client = BluefinClient(
        True,  # agree to terms and conditions
        Networks[TEST_NETWORK],  # network to connect with
        TEST_ACCT_KEY,  # seed phrase of the wallet
    )

    # Initializing client for the private key provided. The second argument api_token is optional
    await client.init(True)

    print("Account Address:", client.get_public_address())

    # gets user account data on-chain
    data = await client.get_user_account_data()
    pprint(data)

    await client.close_connections()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    loop.close()
