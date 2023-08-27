import sys,os
sys.path.append(os.getcwd()+"/src/")
from config import TEST_ACCT_KEY, TEST_SUB_ACCT_KEY, TEST_NETWORK
from bluefin_client_sui import FireflyClient, MARKET_SYMBOLS, ORDER_SIDE, ORDER_TYPE, Networks, OrderSignatureRequest
import asyncio
from bluefin_client_sui.utilities import *


async def main():

  clientParent = FireflyClient(True, Networks[TEST_NETWORK], TEST_ACCT_KEY)
  await clientParent.init(True)

  clientChild = FireflyClient(True, Networks[TEST_NETWORK], TEST_SUB_ACCT_KEY)
  await clientChild.init(True)

  print("Parent: ", clientParent.get_public_address())

  print("Child: ", clientChild.get_public_address())

  # # whitelist sub account
  status = await clientParent.update_sub_account(clientChild.get_public_address(), True)
  print(f"Sub account created: {status}")

  parent_leverage =  await clientParent.get_user_leverage(MARKET_SYMBOLS.ETH)
  await clientParent.adjust_leverage(MARKET_SYMBOLS.ETH,1)
  parent_leverage = await clientParent.get_user_leverage(MARKET_SYMBOLS.ETH)
  signature_request = OrderSignatureRequest(
        symbol=MARKET_SYMBOLS.ETH, # sub account is only whitelisted for ETH market
        maker=clientParent.get_public_address(),  # maker of the order is the parent account
        price=0,  
        quantity=0.02,
        side=ORDER_SIDE.BUY, 
        orderType=ORDER_TYPE.MARKET,
        leverage=parent_leverage,
    )  

  # order is signed using sub account's private key
  signed_order = clientChild.create_signed_order(signature_request) 

  resp = await clientChild.post_signed_order(signed_order)

  print(resp)

  await clientChild.close_connections()
  await clientParent.close_connections()


if __name__ == "__main__":
  loop = asyncio.new_event_loop()
  loop.run_until_complete(main())
  loop.close()