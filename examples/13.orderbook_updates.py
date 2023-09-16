####
## When ever the state of orderbook changes, an event is emitted by exchange.
## In this code example we open a socket connection and listen to orderbook update event
####
import sys, os
sys.path.append(os.getcwd() + "/src/")
import time
from config import TEST_ACCT_KEY, TEST_NETWORK
from bluefin_v2_client import (
    BluefinClient,
    Networks,
    MARKET_SYMBOLS,
    SOCKET_EVENTS,
    ORDER_SIDE,
    ORDER_TYPE,
    ORDER_STATUS,
    OrderSignatureRequest,
)
import asyncio

event_received = False


async def main():

    client = BluefinClient(True, Networks[TEST_NETWORK], TEST_ACCT_KEY)
    await client.init(True)

    def callback(event):
        global event_received
        print("Event data:", event)
        event_received = True

    async def connection_callback():
        # This callback will be invoked as soon as the socket connection is established
        # subscribe to global event updates for BTC market
        status = await client.socket.subscribe_global_updates_by_symbol(MARKET_SYMBOLS.ETH)
        print("Subscribed to global ETH events: {}".format(status))

        # triggered when orderbook updates are received
        print("Listening to orderbook updates")
        await client.socket.listen(SOCKET_EVENTS.ORDERBOOK_UPDATE.value, callback)

    async def disconnection_callback():
        print("Sockets disconnected, performing actions...")
        resp = await client.cancel_all_orders(MARKET_SYMBOLS.ETH, [ORDER_STATUS.OPEN, ORDER_STATUS.PARTIAL_FILLED])
        print(resp)


# must specify connection_callback before opening the sockets below
    await client.socket.listen("connect", connection_callback)
    await client.socket.listen("disconnect", disconnection_callback)

    print("Making socket connection to firefly exchange")
    await client.socket.open()

    ######## Placing an Order ########

    # default leverage of account is set to 3 on firefly
    user_leverage = await client.get_user_leverage(MARKET_SYMBOLS.ETH)

    # creates a MARKET order to be signed
    signature_request = OrderSignatureRequest(
        symbol=MARKET_SYMBOLS.ETH,
        leverage=user_leverage,
        price=1300,
        quantity=0.5,
        side=ORDER_SIDE.BUY,
        orderType=ORDER_TYPE.LIMIT
    )

    # create signed order
    signed_order = client.create_signed_order(signature_request)

    print("Placing a market order")
    # place signed order on orderbook
    resp = await client.post_signed_order(signed_order)
    print(resp)
    ###### Closing socket connections after 30 seconds #####
    timeout = 10
    end_time = time.time() + timeout
    while not event_received and time.time() < end_time:
        time.sleep(1)

    # # close socket connection
    print("Closing sockets!")
    await client.socket.close()


if __name__ == "__main__":
    ### make sure keep the loop initialization same 
    # as below to ensure closing the script after receiving 
    # completion of each callback on socket events ###  
    loop = asyncio.new_event_loop()
    loop.create_task(main())
    pending = asyncio.all_tasks(loop=loop)
    group = asyncio.gather(*pending)
    loop.run_until_complete(group)
    loop.close()
