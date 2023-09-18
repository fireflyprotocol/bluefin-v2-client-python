from pprint import pprint
from config import TEST_ACCT_KEY, TEST_NETWORK
import asyncio
from bluefin_v2_client import (
    BluefinClient,
    ADJUST_MARGIN,
    Networks,
    MARKET_SYMBOLS,
)


async def main():
    client = BluefinClient(True, Networks[TEST_NETWORK], TEST_ACCT_KEY)
    await client.init(True)
    print(await client.get_usdc_balance())

    # Already open positions on exchange can be queried using
    position = await client.get_user_position({"symbol": MARKET_SYMBOLS.ETH})
    pprint(position)

    if not position:
        print("Account has no open position")
        return

    # Add 100 USD from our margin bank into our ETH position on-chain
    print("Adding Margin")
    resp = await client.adjust_margin(MARKET_SYMBOLS.ETH, ADJUST_MARGIN.ADD, 100)
    if resp is False:
        print("Failed to add margin to position")
        pprint(resp)

    # get updated position margin. Note it can take a few seconds to show updates
    # to on-chain positions on exchange as off-chain infrastructure waits for blockchain
    # to emit position update event
    position = await client.get_user_position({"symbol": MARKET_SYMBOLS.ETH})
    print("Current margin in position:", position["margin"])

    # Remove 100 USD from margin
    print(
        "Adjusting margin",
        await client.adjust_margin(MARKET_SYMBOLS.ETH, ADJUST_MARGIN.REMOVE, 100),
    )

    position = await client.get_user_position({"symbol": MARKET_SYMBOLS.ETH})
    print("Current margin in position:", int(position["margin"]))

    await client.close_connections()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    loop.close()
