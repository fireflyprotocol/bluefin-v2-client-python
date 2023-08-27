import sys,os
sys.path.append(os.getcwd()+"/src/")

from config import TEST_ACCT_KEY, TEST_NETWORK
from bluefin_client_sui import FireflyClient, Networks, MARKET_SYMBOLS, ORDER_STATUS
from pprint import pprint
import asyncio

TEST_NETWORK="SUI_STAGING"
async def main():

    client = FireflyClient(True, Networks[TEST_NETWORK], TEST_ACCT_KEY)
    await client.init(True)

    
    # returns user account (having pvt key and pub address)
    user_account = client.get_account()
    print('account:', user_account)

    # returns user public address
    pub_address = client.get_public_address()
    print('pub_address:', pub_address)

    # used to fetch user orders. Pass in statuses of orders to get
    orders = await client.get_orders({
        "symbol": MARKET_SYMBOLS.ETH, 
        "statuses": [ORDER_STATUS.OPEN, ORDER_STATUS.PENDING]
        })

    print("User open and pending orders:")
    pprint(orders)

    # fetches user transaction history. Pass page number and size as the route is paginated
    tx_history = await client.get_transaction_history({
        "symbol": MARKET_SYMBOLS.ETH,
    })
    print("User transaction history:")    
    pprint(tx_history)

    # gets user current position
    position = await client.get_user_position({"symbol":MARKET_SYMBOLS.ETH})

    print("User position:")    
    pprint(position)

    # fetches user trades
    trades = await client.get_user_trades({"symbol":MARKET_SYMBOLS.BTC})
    print("User trades:")    
    pprint(trades)


    # fetches user account's general data like leverage, pnl etc.
    account_data = await client.get_user_account_data()
    print("Account data:")    
    pprint(account_data)


    user_leverage = await client.get_user_leverage(MARKET_SYMBOLS.BTC)
    print("Account leverage:", user_leverage)    

    await client.close_connections()


if __name__ == "__main__":
  loop = asyncio.new_event_loop()
  loop.run_until_complete(main())
  loop.close()