import sys, os

# sys.path.append(os.getcwd() + "/src/")

from config import TEST_ACCT_KEY, TEST_NETWORK
from bluefin_v2_client import BluefinClient, Networks
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

    # checks chain native token balance.
    # A user must have native tokens to perform contract calls

    print("Chain token balance:", await client.get_native_chain_token_balance())

    # check margin bank balance on-chain
    print("Margin bank balance:", await client.get_margin_bank_balance())

    # check usdc balance user has on-chain
    print("USDC balance:", await client.get_usdc_balance())

    # deposit usdc to margin bank
    # must have native chain tokens to pay for gas fee
    usdc_coins = client.get_usdc_coins()
    ## we expect that you have some coins in your usdc,
    coin_obj_id = usdc_coins["data"][1]["coinObjectId"]
    print("USDC deposited:", await client.deposit_margin_to_bank(5000, coin_obj_id))

    # check margin bank balance
    resp = await client.get_margin_bank_balance()
    print("Margin bank balance:", resp)

    # withdraw margin bank balance
    print("USDC Withdrawn:", await client.withdraw_margin_from_bank(10))

    # check margin bank balance
    print("Margin bank balance:", await client.get_margin_bank_balance())

    print("Withdraw all", await client.withdraw_all_margin_from_bank())

    print("Margin bank balance:", await client.get_margin_bank_balance())
    await client.close_connections()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    loop.close()
