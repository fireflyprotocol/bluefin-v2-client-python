import sys,os
sys.path.append(os.getcwd()+"/src/")

from config import TEST_ACCT_KEY, TEST_NETWORK
from bluefin_client_sui import FireflyClient, Networks, MARKET_SYMBOLS
import asyncio


async def main():

    # initialize client
    client = FireflyClient(
        True, # agree to terms and conditions
        Networks[TEST_NETWORK], # network to connect with
        TEST_ACCT_KEY # private key of wallet

    )

    await client.init(True, symbol= MARKET_SYMBOLS.BTC) 

    print('Leverage on BTC market:', await client.get_user_leverage(MARKET_SYMBOLS.BTC))
    # we have a position on BTC so this will perform on-chain leverage update
    # must have native chain tokens to pay for gas fee
    await client.adjust_leverage(MARKET_SYMBOLS.BTC, 6) 

    print('Leverage on BTC market:', await client.get_user_leverage(MARKET_SYMBOLS.BTC))

        # initialize client
    client = FireflyClient(
        True, # agree to terms and conditions
        Networks[TEST_NETWORK], # network to connect with
        TEST_ACCT_KEY, # private key of wallet
    )

    await client.init(True, symbol=MARKET_SYMBOLS.ETH) 

    print('Leverage on ETH market:', await client.get_user_leverage(MARKET_SYMBOLS.ETH))
    # since we don't have a position on-chain, it will perform off-chain leverage adjustment
    await client.adjust_leverage(MARKET_SYMBOLS.ETH, 7) 

    print('Leverage on ETH market:', await client.get_user_leverage(MARKET_SYMBOLS.ETH))
    
    await client.close_connections()

if __name__ == "__main__":
  loop = asyncio.new_event_loop()
  loop.run_until_complete(main())
  loop.close()