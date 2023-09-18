from pprint import pprint
import asyncio
import time
import random
from config import TEST_ACCT_KEY, TEST_NETWORK
from bluefin_v2_client import (
    BluefinClient,
    Networks,
    MARKET_SYMBOLS,
    ORDER_SIDE,
    ORDER_TYPE,
    ORDER_STATUS,
    OrderSignatureRequest,
)


async def main():
    client = BluefinClient(True, Networks[TEST_NETWORK], TEST_ACCT_KEY)
    await client.init(True)

    leverage = 1
    await client.adjust_leverage(MARKET_SYMBOLS.ETH, leverage)
    order = OrderSignatureRequest(
        symbol=MARKET_SYMBOLS.ETH,  # market symbol
        price=2905,  # price at which you want to place order
        quantity=0.01,  # quantity
        side=ORDER_SIDE.BUY,
        orderType=ORDER_TYPE.LIMIT,
        leverage=leverage,
        salt=random.randint(0, 100000000),
        expiration=int(time.time() + (30 * 24 * 60 * 60)) * 1000,
    )
    signed_order = client.create_signed_order(order)
    post_resp = await client.post_signed_order(signed_order)
    pprint(post_resp)
    time.sleep(2)

    # cancel placed order
    cancellation_request = client.create_signed_cancel_orders(
        MARKET_SYMBOLS.ETH, order_hash=[post_resp["hash"]]
    )
    cancellation_request = client.create_signed_cancel_order(order)
    pprint(cancellation_request)
    cancel_resp = await client.post_cancel_order(cancellation_request)
    pprint(cancel_resp)

    # post order again
    await client.adjust_leverage(MARKET_SYMBOLS.ETH, leverage)
    order = OrderSignatureRequest(
        symbol=MARKET_SYMBOLS.ETH,  # market symbol
        price=2905,  # price at which you want to place order
        quantity=0.01,  # quantity
        side=ORDER_SIDE.BUY,
        orderType=ORDER_TYPE.LIMIT,
        leverage=leverage,
        salt=random.randint(0, 100000000),
        expiration=int(time.time() + (30 * 24 * 60 * 60)) * 1000,
    )
    signed_order = client.create_signed_order(order)
    post_resp = await client.post_signed_order(signed_order)
    pprint(post_resp)
    time.sleep(2)

    # this time cancel all open orders
    resp = await client.cancel_all_orders(
        MARKET_SYMBOLS.ETH, [ORDER_STATUS.OPEN, ORDER_STATUS.PARTIAL_FILLED]
    )
    if resp is False:
        print("No open order to cancel")
    else:
        pprint(resp)

    await client.close_connections()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    loop.close()
