from pprint import pprint
import asyncio
from config import TEST_ACCT_KEY, TEST_NETWORK
from bluefin_v2_client import BluefinClient, Networks


async def main():
    # create client instance
    client = BluefinClient(
        True,  # agree to terms and conditions
        Networks[TEST_NETWORK],  # network to connect with
        TEST_ACCT_KEY,  # seed phrase of the wallet
    )

    # initialize the client
    # on boards user on Bluefin. Must be set to true for first time use
    await client.init(True)

    # checks SUI token balance
    print("Chain token balance:", await client.get_native_chain_token_balance())

    # check usdc balance deposited to Bluefin Margin Bank
    print("Margin bank balance:", await client.get_margin_bank_balance())

    # check usdc balance deposited to USDC contract
    print("USDC balance:", await client.get_usdc_balance())

    usdc_coins = await client.get_usdc_coins()
    pprint(usdc_coins)

    # deposit 100 usdc to margin bank
    print("USDC deposited:", await client.deposit_margin_to_bank(100))

    # check margin bank balance
    resp = await client.get_margin_bank_balance()
    print("Margin bank balance after deposit:", resp)

    # withdraw margin bank balance
    print("USDC Withdrawn:", await client.withdraw_margin_from_bank(100))

    # check margin bank balance
    print("Margin bank balance after withdraw:", await client.get_margin_bank_balance())

    # print("Withdraw all", await client.withdraw_all_margin_from_bank())

    # print("Margin bank balance:", await client.get_margin_bank_balance())
    await client.close_connections()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    loop.close()
