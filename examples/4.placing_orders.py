from pprint import pprint
import asyncio
import time
from config import TEST_ACCT_KEY, TEST_NETWORK
from bluefin_v2_client import (
    BluefinClient,
    Networks,
    MARKET_SYMBOLS,
    ORDER_SIDE,
    ORDER_TYPE,
    OrderSignatureRequest,
)


async def place_orders(client: BluefinClient):
    # default leverage of account is set to 3 on Bluefin
    user_leverage = await client.get_user_leverage(MARKET_SYMBOLS.ETH)
    print("User Default Leverage", user_leverage)

    # Sign and place a limit order at 4x leverage. Order is signed using the account seed phrase set on the client
    adjusted_leverage = 4
    await client.adjust_leverage(MARKET_SYMBOLS.ETH, adjusted_leverage)
    signature_request = OrderSignatureRequest(
        symbol=MARKET_SYMBOLS.ETH,  # market symbol
        price=1636.8,  # price at which you want to place order
        quantity=0.01,  # quantity
        side=ORDER_SIDE.BUY,
        orderType=ORDER_TYPE.LIMIT,
        leverage=adjusted_leverage,
        expiration=int(
            (time.time() + 864000) * 1000
        ),  # expiry after 10 days, default expiry is a month
    )
    signed_order = client.create_signed_order(signature_request)
    resp = await client.post_signed_order(signed_order)
    pprint({"msg": "placing limit order", "resp": resp})

    # sign and place a market order at 2x leverage
    adjusted_leverage = 2
    await client.adjust_leverage(MARKET_SYMBOLS.BTC, adjusted_leverage)
    signature_request = OrderSignatureRequest(
        symbol=MARKET_SYMBOLS.BTC,
        price=0,
        quantity=1,
        leverage=adjusted_leverage,
        side=ORDER_SIDE.BUY,
        reduceOnly=False,
        postOnly=False,
        cancelOnRevert= False,
        orderbookOnly=True,
        orderType=ORDER_TYPE.MARKET,
    )
    signed_order = client.create_signed_order(signature_request)
    resp = await client.post_signed_order(signed_order)
    pprint({"msg": "placing market order", "resp": resp})
    return


async def main():
    # initialize client
    client = BluefinClient(
        True,  # agree to terms and conditions
        Networks[TEST_NETWORK],  # network to connect with
        TEST_ACCT_KEY,  # seed phrase of the wallet
    )

    await client.init(True)
    await place_orders(client)

    await client.close_connections()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    loop.close()
