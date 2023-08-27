"""
    This example shows how users can get their orders information.
    The get_orders route provides a number of optional params that can be 
    mixed together to fetch the exact data that user needs.
"""
import sys, os

sys.path.append(os.getcwd() + "/src/")
from config import TEST_ACCT_KEY, TEST_NETWORK
from bluefin_client_sui import (
    BluefinClient,
    Networks,
    MARKET_SYMBOLS,
    ORDER_STATUS,
    ORDER_TYPE,
)
import asyncio


async def main():
    client = BluefinClient(True, Networks[TEST_NETWORK], TEST_ACCT_KEY)
    await client.init(True)

    print("Get all ETH market orders regardless of their type/status")
    orders = await client.get_orders(
        {
            "symbol": MARKET_SYMBOLS.ETH,
        }
    )
    print("Received orders: ", len(orders))

    print("Get orders based on status (OPEN and PENDING)")
    orders = await client.get_orders(
        {
            "symbol": MARKET_SYMBOLS.ETH,
            "statuses": [ORDER_STATUS.OPEN, ORDER_STATUS.PENDING],
        }
    )
    print("Received orders: ", len(orders))

    print("Get an order 180318 using id (possible this order is not available anymore)")
    orders = await client.get_orders({"symbol": MARKET_SYMBOLS.ETH, "orderId": 180318})
    print("Received orders: ", len(orders))

    print("Get orders using hashes (possible these orders are not available anymore)")
    orders = await client.get_orders(
        {
            "symbol": MARKET_SYMBOLS.ETH,
            "orderHashes": [
                "0x21eeb24b0af6832989484e61294db70e8cf8ce0e030c6cfbbb23f3b3d85f9374",
                "0xd61fe390f6e6d89a884c73927741ba7d2d024e01f65af61f13363403e805e2c0",
            ],
        }
    )
    print("Received orders: ", len(orders))

    print("Get only MARKET orders for ETH market")
    orders = await client.get_orders(
        {"symbol": MARKET_SYMBOLS.ETH, "orderType": [ORDER_TYPE.MARKET]}
    )
    print("Received orders: ", len(orders))

    await client.close_connections()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    loop.close()
