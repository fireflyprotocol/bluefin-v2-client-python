import sys,os
sys.path.append(os.getcwd()+"/src/")
import base64
from bluefin_client_sui.utilities import *
from config import TEST_ACCT_KEY, TEST_NETWORK
from bluefin_client_sui import FireflyClient, Networks, MARKET_SYMBOLS, ORDER_SIDE, ORDER_TYPE, OrderSignatureRequest
import asyncio
from bluefin_client_sui import signer
from bluefin_client_sui import *

async def main():

    # initialize client
    client = FireflyClient(
        True, # agree to terms and conditions
        Networks[TEST_NETWORK], # network to connect with
        TEST_ACCT_KEY, # private key of wallet
        )
    await client.init(True) 
    ### you need to have usdc coins to deposit it to margin bank.
    ### the below functions just gets usdc coins that you have.
    usdc_coins=client.get_usdc_coins()

    coin_obj_id=usdc_coins["data"][1]["coinObjectId"]
    await client.deposit_margin_to_bank(1000, coin_obj_id) 
    

    #await client.withdraw_margin_from_bank(100)
    
    
    #await client.withdraw_all_margin_from_bank()

    print ("Printing Margin Bank balance")
    print (await client.get_margin_bank_balance())

    print ("Printing usdc balance")
    print (await client.get_usdc_balance())

    print ("Printing SUI balance")
    print (await client.get_native_chain_token_balance())


    print ("getting usdc coins")
    print (client.get_usdc_coins())





    await client.close_connections()
    



if __name__ == "__main__":
  loop = asyncio.new_event_loop()
  loop.run_until_complete(main())
  loop.close()