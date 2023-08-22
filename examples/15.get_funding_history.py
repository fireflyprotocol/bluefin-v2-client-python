
import sys,os
sys.path.append(os.getcwd()+"/src/")
from config import TEST_ACCT_KEY, TEST_NETWORK
from bluefin_client_sui import FireflyClient, Networks, MARKET_SYMBOLS, GetFundingHistoryRequest
from pprint import pprint
import asyncio

async def main():
    client = FireflyClient(True, Networks[TEST_NETWORK], TEST_ACCT_KEY)
    await client.init(True)
 

    # create a funding history request
    funding_history_request = GetFundingHistoryRequest(
        symbol=MARKET_SYMBOLS.ETH,  # market symbol
        pageSize=50, # gets provided number of payments <= 50
        cursor=0 # fetch a particular page. A single page contains upto 50 records
    )

    # submit request for funding history
    funding_history_response = await client.get_funding_history(funding_history_request)

    # returns funding history response
    pprint(funding_history_response)

    await client.close_connections()


if __name__ == "__main__":
  loop = asyncio.new_event_loop()
  loop.run_until_complete(main())
  loop.close()