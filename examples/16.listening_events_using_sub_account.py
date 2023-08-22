'''
  This example shows how you can listen to user events using sub account
  On our exchange, a sub account is trading on its parent's position and thus
  has no position of its own. So when placing orders or listening to position updates
  the sub account must specify the parent address whose position its listening.
'''
import time, sys
from config import TEST_ACCT_KEY, TEST_NETWORK, TEST_SUB_ACCT_KEY
from bluefin_client_sui import FireflyClient, Networks, MARKET_SYMBOLS, OrderSignatureRequest, ORDER_SIDE, ORDER_TYPE, SOCKET_EVENTS
import asyncio

def callback(event):
    print("Event data: {}\n".format(event))

async def main():

  clientParent = FireflyClient(True, Networks[TEST_NETWORK], TEST_ACCT_KEY)
  await clientParent.init(True)

  clientChild = FireflyClient(True, Networks[TEST_NETWORK], TEST_SUB_ACCT_KEY)
  await clientChild.init(True)

  print("Parent: ", clientParent.get_public_address())

  print("Child: ", clientChild.get_public_address())

  # # whitelist sub account
  status = await clientParent.update_sub_account(MARKET_SYMBOLS.ETH, clientChild.get_public_address(), True)
  print("Sub account created: {}\n".format(status))


  # must open socket before subscribing
  print("Making socket connection to firefly exchange")
  await clientChild.socket.open()

  # subscribe to parent's events
  resp = await clientChild.socket.subscribe_user_update_by_token(clientParent.get_public_address())
  print("Subscribed to parent's events:",resp)


  # triggered when status of any user order updates
  print("Listening to parents position updates")
  await clientChild.socket.listen(SOCKET_EVENTS.POSITION_UPDATE.value, callback)

  clientChild.add_market(MARKET_SYMBOLS.ETH)

  parent_leverage =  await clientParent.get_user_leverage(MARKET_SYMBOLS.ETH)

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

  time.sleep(10)

  status = await clientChild.socket.unsubscribe_user_update_by_token(clientParent.get_public_address())
  print("Unsubscribed from user events: {}".format(status))

  # close socket connection
  print("Closing sockets!")
  await clientChild.socket.close()
  
  await clientChild.close_connections()
  await clientParent.close_connections()


if __name__ == "__main__":
  loop = asyncio.new_event_loop()
  loop.run_until_complete(main())
  loop.close()