import sys, os

sys.path.append(os.getcwd() + "/src/")

import time
from config import TEST_ACCT_KEY, TEST_NETWORK
from bluefin_client_sui import BluefinClient, Networks, MARKET_SYMBOLS, SOCKET_EVENTS
import asyncio

TEST_NETWORK = "SUI_STAGING"
event_received = False


def callback(event):
    global event_received
    print("Event data:", event)
    event_received = True


async def main():
    client = BluefinClient(True, Networks[TEST_NETWORK], TEST_ACCT_KEY)
    await client.init(True)

    async def my_callback():
        print("Subscribing To Rooms")
        # subscribe to global event updates for BTC market
        status = await client.socket.subscribe_global_updates_by_symbol(
            MARKET_SYMBOLS.BTC
        )
        print("Subscribed to global BTC events: {}".format(status))

        # subscribe to local user events
        status = await client.socket.subscribe_user_update_by_token()
        print("Subscribed to user events: {}".format(status))

        # triggered when order book updates
        print("Listening to exchange health updates")
        await client.socket.listen(SOCKET_EVENTS.EXCHANGE_HEALTH.value, callback)

        # triggered when status of any user order updates
        print("Listening to user order updates")
        await client.socket.listen(SOCKET_EVENTS.ORDER_UPDATE.value, callback)

    await client.socket.listen("connect", my_callback)

    # must open socket before subscribing
    print("Making socket connection to Bluefin exchange")
    await client.socket.open()

    # SOCKET_EVENTS contains all events that can be listened to

    # logs event name and data for all markets and users that are subscribed.
    # helpful for debugging
    # client.socket.listen("default",callback)
    timeout = 30
    end_time = time.time() + timeout
    while not event_received and time.time() < end_time:
        time.sleep(1)

    # # unsubscribe from global events
    status = await client.socket.unsubscribe_global_updates_by_symbol(
        MARKET_SYMBOLS.BTC
    )
    print("Unsubscribed from global BTC events: {}".format(status))

    status = await client.socket.unsubscribe_user_update_by_token()
    print("Unsubscribed from user events: {}".format(status))

    # # close socket connection
    print("Closing sockets!")
    await client.socket.close()

    await client.apis.close_session()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    loop.close()
