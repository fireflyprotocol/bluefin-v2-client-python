import sys,os
sys.path.append(os.getcwd()+"/src/")
from bluefin_client_sui.utilities import toSuiBase
from config import TEST_ACCT_KEY, TEST_NETWORK
from bluefin_client_sui import FireflyClient, Networks, MARKET_SYMBOLS, ORDER_SIDE, ORDER_TYPE, OrderSignatureRequest
import asyncio



async def place_limit_order(client: FireflyClient):
   
    # default leverage of account is set to 3 on firefly
    user_leverage = await client.get_user_leverage(MARKET_SYMBOLS.ETH)

    # creates a LIMIT order to be signed
    signature_request = OrderSignatureRequest(
        symbol=MARKET_SYMBOLS.ETH,  # market symbol
        price=toSuiBase(1636.8),  # price at which you want to place order
        quantity=toSuiBase(0.01), # quantity
        side=ORDER_SIDE.BUY, 
        orderType=ORDER_TYPE.LIMIT,
        leverage=toSuiBase(1)
    )  

    # create signed order
    signed_order = client.create_signed_order(signature_request) 

    print("Placing a limit order")
    # place signed order on orderbook
    resp = await client.post_signed_order(signed_order)

    # returned order with PENDING state
    print(resp)

    return

async def place_market_order(client: FireflyClient):
    

    # default leverage of account is set to 3 on firefly
    user_leverage = await client.get_user_leverage(MARKET_SYMBOLS.ETH)

    # creates a LIMIT order to be signed
    '''
    signature_request = OrderSignatureRequest(
        symbol=MARKET_SYMBOLS.ETH,  # market symbol
        price=0,  # price at which you want to place order
        quantity=0.01, # quantity
        side=ORDER_SIDE.BUY, 
        orderType=ORDER_TYPE.MARKET,
        leverage=user_leverage
    ) '''
    signature_request = OrderSignatureRequest(
        symbol=MARKET_SYMBOLS.ETH,
       # market = "0x25a869797387e2eaa09c658c83dc0deaba99bb02c94447339c06fdbe8287347e",
        price = toSuiBase(0),
        quantity = toSuiBase(1),
        leverage = toSuiBase(1),
        side = ORDER_SIDE.BUY,
        reduceOnly = False,
        postOnly = False,
        orderbookOnly = True,
        maker = "0xa3c3504d90c428274beaa89f1238a769ea1d1c3516c31c0f4157f33787367af0",
        expiration = 1700530261000,
        salt = 1668690862116,
        orderType = ORDER_TYPE.MARKET,
    )

    # create signed order
    signed_order = client.create_signed_order(signature_request) 

    print("Placing a market order")
    # place signed order on orderbook
    resp = await client.post_signed_order(signed_order)

    # returned order with PENDING state
    print(resp)


    return

async def main():

    # initialize client
    client = FireflyClient(
        True, # agree to terms and conditions
        Networks[TEST_NETWORK], # network to connect with
        TEST_ACCT_KEY, # private key of wallet
        )

    await client.init(True) 

    # add market that you wish to trade on ETH/BTC are supported currently
    client.add_market(MARKET_SYMBOLS.ETH)

    # await place_limit_order(client)
    await place_market_order(client)
    await place_limit_order(client)
    
    await client.close_connections()


if __name__ == "__main__":
  loop = asyncio.new_event_loop()
  loop.run_until_complete(main())
  loop.close()