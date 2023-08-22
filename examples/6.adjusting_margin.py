import sys,os
sys.path.append(os.getcwd()+"/src/")

from config import TEST_ACCT_KEY, TEST_NETWORK
from bluefin_client_sui import FireflyClient, Networks, MARKET_SYMBOLS, ADJUST_MARGIN
from eth_utils import from_wei
import asyncio

TEST_NETWORK="SUI_STAGING"
async def main():

    client = FireflyClient(True, Networks[TEST_NETWORK], TEST_ACCT_KEY)
    await client.init(True)

    position = await client.get_user_position({"symbol":MARKET_SYMBOLS.ETH}) 
    print("Current margin in position:", from_wei(int(position["margin"]), "ether"))

    # adding 100$ from our margin bank into our BTC position on-chain
    # must have native chain tokens to pay for gas fee
    await client.adjust_margin(MARKET_SYMBOLS.ETH, ADJUST_MARGIN.ADD, 100) 

    # get updated position margin. Note it can take a few seconds to show updates
    # to on-chain positions on exchange as off-chain infrastructure waits for blockchain
    # to emit position update event
    position = await client.get_user_position({"symbol":MARKET_SYMBOLS.ETH}) 
    print("Current margin in position:", from_wei(int(position["margin"]), "ether"))


    # removing 100$ from margin
    await client.adjust_margin(MARKET_SYMBOLS.ETH, ADJUST_MARGIN.REMOVE, 100) 

    position = await client.get_user_position({"symbol":MARKET_SYMBOLS.ETH}) 
    print("Current margin in position:", from_wei(int(position["margin"]), "ether"))


    try:
        # will throw as user does not have any open position on BTC to adjust margin on
        await client.adjust_margin(MARKET_SYMBOLS.BTC, ADJUST_MARGIN.ADD, 100) 
    except Exception as e:
        print("Error:", e)

    await client.close_connections()


if __name__ == "__main__":
  loop = asyncio.new_event_loop()
  loop.run_until_complete(main())
  loop.close()