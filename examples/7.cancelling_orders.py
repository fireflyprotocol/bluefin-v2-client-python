import sys,os, random
sys.path.append(os.getcwd()+"/src/")

import time
from config import TEST_ACCT_KEY, TEST_NETWORK
from bluefin_client_sui.utilities import toSuiBase
from bluefin_client_sui import FireflyClient, Networks, MARKET_SYMBOLS, ORDER_SIDE, ORDER_TYPE, ORDER_STATUS, OrderSignatureRequest
from pprint import pprint
import asyncio



async def main():

    client = FireflyClient(True, Networks[TEST_NETWORK], TEST_ACCT_KEY)
    await client.init(True)

    # must add market before cancelling its orders
    client.add_market(MARKET_SYMBOLS.ETH)
    #client.create_order_to_sign()
    #await client.adjust_leverage(MARKET_SYMBOLS.ETH, 1) 

    order = {
        #"market": "0x25a869797387e2eaa09c658c83dc0deaba99bb02c94447339c06fdbe8287347e",
        "symbol":MARKET_SYMBOLS.ETH, 
        "price": toSuiBase(1000), 
        "quantity":toSuiBase(1), 
        "side":ORDER_SIDE.SELL, 
        "orderType":ORDER_TYPE.LIMIT,
        "leverage":toSuiBase(1),
        "expiration":int(time.time()+(30*24*60*60))*1000, # a random time in future
        "reduceOnly":False,
        "salt":111000000,
        "postOnly":False,
        "orderType": ORDER_TYPE.LIMIT,
        "orderbookOnly": True

    }
        # creates a LIMIT order to be signed
    order = OrderSignatureRequest(
        symbol=MARKET_SYMBOLS.ETH,  # market symbol
        price=toSuiBase(1636.8),  # price at which you want to place order
        quantity=toSuiBase(0.01), # quantity
        side=ORDER_SIDE.BUY, 
        orderType=ORDER_TYPE.LIMIT,
        leverage=toSuiBase(1),
        salt=random.randint(0,100000000),
        expiration=int(time.time()+(30*24*60*60))*1000
    ) 


    signed_order = client.create_signed_order(order) 
    resp = await client.post_signed_order(signed_order)
    
    
    # sign order for cancellation using order hash
    # you can pass a list of hashes to be signed for cancellation, good to be used when multiple orders are to be cancelled
    cancellation_request = client.create_signed_cancel_orders(MARKET_SYMBOLS.ETH, order_hash=[resp['hash']])
    pprint(cancellation_request)

    # # or sign the order for cancellation using order data
    cancellation_request = client.create_signed_cancel_order(order)
    pprint(cancellation_request) # same as above cancellation request

    # post order to exchange for cancellation
    resp = await client.post_cancel_order(cancellation_request)
    
    pprint(resp)

    # cancels all open orders, returns false if there is no open order to cancel
    resp = await client.cancel_all_orders(MARKET_SYMBOLS.ETH, [ORDER_STATUS.OPEN, ORDER_STATUS.PARTIAL_FILLED])

    if resp == False:
        print('No open order to cancel')
    else:
        pprint(resp)

    await client.close_connections()


if __name__ == "__main__":
  loop = asyncio.new_event_loop()
  loop.run_until_complete(main())
  loop.close()