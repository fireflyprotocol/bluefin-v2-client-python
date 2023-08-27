'''
The code example opens socket connection and listens to user order update events
It places a limit order and as soon as its OPENED on order book, we receive
an event, log its data and terminate connection
'''
import sys,os
sys.path.append(os.getcwd()+"/src/")
import time
from config import TEST_ACCT_KEY, TEST_NETWORK
from bluefin_client_sui import FireflyClient, Networks, MARKET_SYMBOLS, SOCKET_EVENTS, ORDER_SIDE, ORDER_TYPE, OrderSignatureRequest
import asyncio
TEST_NETWORK="SUI_STAGING"

event_received = False




async def place_limit_order(client:FireflyClient):
       
    # default leverage of account is set to 3 on firefly
    await client.adjust_leverage(MARKET_SYMBOLS.ETH,1)
    user_leverage = await client.get_user_leverage(MARKET_SYMBOLS.ETH)
    

    # creates a LIMIT order to be signed
    signature_request = OrderSignatureRequest(
        symbol=MARKET_SYMBOLS.ETH,  # market symbol
        price=1300000000000,  # price at which you want to place order
        quantity=10000000, # quantity
        side=ORDER_SIDE.SELL, 
        orderType=ORDER_TYPE.LIMIT,
        leverage=1000000000
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

    client = FireflyClient(True, Networks[TEST_NETWORK], TEST_ACCT_KEY)
    await client.init(True)

    def callback(event):
        global event_received
        print("Event data:", event)
        event_received = True


    # must open socket before subscribing
    print("Making socket connection to firefly exchange")
    await client.socket.open()

    # subscribe to user events 
    await client.socket.subscribe_user_update_by_token()
    print("Subscribed to user events")

    print("Listening to user order updates")
    await client.socket.listen(SOCKET_EVENTS.ORDER_UPDATE.value, callback)
    
    # place a limit order
    await place_limit_order(client)

    timeout = 30
    end_time = time.time() + timeout
    while not event_received and time.time() < end_time:
        time.sleep(1)

    status = await client.socket.unsubscribe_user_update_by_token()
    print("Unsubscribed from user events: {}".format(status))

    # close socket connection
    print("Closing sockets!")
    await client.socket.close()

    await client.close_connections()



if __name__ == "__main__":
  loop = asyncio.new_event_loop()
  loop.run_until_complete(main())
  loop.close()

