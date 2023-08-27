"""
When ever the state of orderbook changes, an event is emitted by exchange.
In this code example we open a socket connection and listen to orderbook update event
"""
import sys, os

sys.path.append(os.getcwd() + "/src/")
import time
from config import TEST_ACCT_KEY, TEST_NETWORK
from bluefin_client_sui import (
    BluefinClient,
    Networks,
    MARKET_SYMBOLS,
    SOCKET_EVENTS,
    ORDER_SIDE,
    ORDER_TYPE,
    OrderSignatureRequest,
)
import asyncio

TEST_NETWORK = "SUI_STAGING"

event_received = False


async def place_limit_order(client: BluefinClient):
    # default leverage of account is set to 3 on Bluefin
    user_leverage = await client.get_user_leverage(MARKET_SYMBOLS.ETH)

    # creates a LIMIT order to be signed
    signature_request = OrderSignatureRequest(
        symbol=MARKET_SYMBOLS.ETH,  # market symbol
        price=1300,  # price at which you want to place order
        quantity=0.01,  # quantity
        side=ORDER_SIDE.SELL,
        orderType=ORDER_TYPE.LIMIT,
        leverage=user_leverage,
    )
    # create signed order
    signed_order = client.create_signed_order(signature_request)

    print("Placing a limit order")
    # place signed order on orderbook
    resp = await client.post_signed_order(signed_order)

    # returned order with PENDING state
    print(resp)
    return


async def main():
    client = BluefinClient(True, Networks[TEST_NETWORK], TEST_ACCT_KEY)
    await client.init(True)

    def callback(event):
        global event_received
        print("Event data:", event)
        event_received = True

    # must open socket before subscribing
    print("Making socket connection to Bluefin exchange")
    await client.socket.open()

    # subscribe to global event updates for ETH market
    await client.socket.subscribe_global_updates_by_symbol(MARKET_SYMBOLS.ETH)
    print("Subscribed to ETH Market events")

    print("Listening to ETH Orderbook update event")
    await client.socket.listen(SOCKET_EVENTS.ORDERBOOK_UPDATE.value, callback)

    await place_limit_order(client)

    timeout = 30
    end_time = time.time() + timeout
    while not event_received and time.time() < end_time:
        time.sleep(1)
    status = await client.socket.unsubscribe_global_updates_by_symbol(
        MARKET_SYMBOLS.ETH
    )
    print("Unsubscribed from orderbook update events for ETH Market: {}".format(status))

    # close socket connection
    print("Closing sockets!")
    await client.socket.close()

    await client.close_connections()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    loop.close()
