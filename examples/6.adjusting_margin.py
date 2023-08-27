import sys,os
sys.path.append(os.getcwd()+"/src/")

from config import TEST_ACCT_KEY, TEST_NETWORK
from bluefin_client_sui import FireflyClient, Networks, MARKET_SYMBOLS, ADJUST_MARGIN
import asyncio
from bluefin_client_sui import FireflyClient, Networks, MARKET_SYMBOLS, ORDER_SIDE, ORDER_TYPE, OrderSignatureRequest
TEST_NETWORK="SUI_STAGING"

async def place_limit_order(client: FireflyClient):

    # default leverage of account is set to 3 on firefly
    user_leverage = await client.get_user_leverage(MARKET_SYMBOLS.ETH)
    await client.adjust_leverage(MARKET_SYMBOLS.ETH, 3)
    user_leverage = await client.get_user_leverage(MARKET_SYMBOLS.ETH)

    print ("User Leverage", user_leverage)
    

    # creates a LIMIT order to be signed
    signature_request = OrderSignatureRequest(
        symbol=MARKET_SYMBOLS.ETH,  # market symbol
        price=1636.8,  # price at which you want to place order
        quantity=0.01, # quantity
        side=ORDER_SIDE.BUY, 
        orderType=ORDER_TYPE.LIMIT,
        leverage=user_leverage
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

    signature_request = OrderSignatureRequest(
        symbol=MARKET_SYMBOLS.ETH,
        price = 0,
        quantity = 1,
        leverage = user_leverage,
        side = ORDER_SIDE.BUY,
        orderType=ORDER_TYPE.MARKET,
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

    client = FireflyClient(True, Networks[TEST_NETWORK], TEST_ACCT_KEY)
    await client.init(True)
    print (await client.get_usdc_balance())
    
    #usdc_coins=client.get_usdc_coins()
    #coin_obj_id=usdc_coins["data"][1]["coinObjectId"]
    #await client.deposit_margin_to_bank(1000000000000, coin_obj_id) 
  
    print (await client.get_margin_bank_balance())
    await place_market_order(client)

    position = await client.get_user_position({"symbol":MARKET_SYMBOLS.ETH}) 
    print("Current margin in position:", position)

    # adding 100$ from our margin bank into our BTC position on-chain
    # must have native chain tokens to pay for gas fee
    await client.adjust_margin(MARKET_SYMBOLS.ETH, ADJUST_MARGIN.ADD, 100) 

    # get updated position margin. Note it can take a few seconds to show updates
    # to on-chain positions on exchange as off-chain infrastructure waits for blockchain
    # to emit position update event
    position = await client.get_user_position({"symbol":MARKET_SYMBOLS.ETH}) 
    print("Current margin in position:",position["margin"])


    # removing 100$ from margin
    await client.adjust_margin(MARKET_SYMBOLS.ETH, ADJUST_MARGIN.REMOVE, 100) 

    position = await client.get_user_position({"symbol":MARKET_SYMBOLS.ETH}) 
    print("Current margin in position:", int(position["margin"]))


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