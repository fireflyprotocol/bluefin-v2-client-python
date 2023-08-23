import sys,os
sys.path.append(os.getcwd()+"/src/")

from config import TEST_ACCT_KEY, TEST_NETWORK
from bluefin_client_sui import FireflyClient, Networks, MARKET_SYMBOLS, TRADE_TYPE, Interval
from pprint import pprint
import asyncio


async def main():

    client = FireflyClient(True, Networks[TEST_NETWORK], TEST_ACCT_KEY)
    await client.init(True)


    # returns status/health of exchange
    status = await client.get_exchange_status()
    pprint(status)

    # gets state of order book. Gets first 10 asks and bids
    orderbook = await client.get_orderbook({"symbol": MARKET_SYMBOLS.ETH, "limit":10})
    pprint(orderbook)

    # returns available market for trading
    market_symbols = await client.get_market_symbols()
    print(market_symbols)

    # gets current funding rate on market
    funding_rate = await client.get_funding_rate(MARKET_SYMBOLS.ETH)
    pprint(funding_rate)

    # gets markets meta data about contracts, blockchain, exchange url
    meta = await client.get_market_meta_info() # (optional param MARKET_SYMBOL)
    # should log meta for all markets
    pprint(meta)

    # gets market's current state
    market_data = await client.get_market_data(MARKET_SYMBOLS.ETH)
    pprint(market_data)


    # gets market data about min/max order size, oracle price, fee etc..
    exchange_info = await client.get_exchange_info(MARKET_SYMBOLS.ETH)
    pprint(exchange_info)

    # gets market candle info
    candle_data = await client.get_market_candle_stick_data({"symbol": MARKET_SYMBOLS.ETH, "interval": Interval._1M})
    pprint(candle_data)

    # gets recent isolated/normal trades on ETH market
    recent_trades = await client.get_market_recent_trades({"symbol": MARKET_SYMBOLS.ETH, "traders": TRADE_TYPE.ISOLATED})
    pprint(recent_trades)


    # gets addresses of on-chain contracts
    contract_address = await client.get_contract_addresses()
    pprint(contract_address)

    await client.close_connections()


if __name__ == "__main__":
  loop = asyncio.new_event_loop()
  loop.run_until_complete(main())
  loop.close()