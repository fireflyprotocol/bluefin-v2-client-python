# Changes w.r.t old library

## Initialisation change

1. The way we initialise is still the same, the difference is that NOW we give `SEED_PHRASE` as `TEST_ACCT_KEY`
2. Currently we support test phrase only and we sign it using ED25519

## Sockets

1. Nothing is changes in sockets except for the url link

## Signing (internal)

1. We do not sign our transaction using ETH library anymore. We now use `nacl` and `hashlib` in order to sign the messages.
2. For signing orders we sign it using the following scheme

   1. Assuming we have the order with values in sui format.
   2. We first get the `orderhash` of the order using the following method

      ```python flags = self.get_order_flags(order)
        flags = hexToByteArray(numberToHex(flags,2))

        buffer=bytearray()
        orderPriceHex=hexToByteArray(numberToHex(int(order["price"])))
        orderQuantityHex=hexToByteArray(numberToHex(int(order['quantity'])))
        orderLeverageHex=hexToByteArray (numberToHex(int(order['leverage'])))
        orderSalt=hexToByteArray(numberToHex(int(order['salt'])))
        orderExpiration=hexToByteArray(numberToHex(int(order['expiration']),16))
        orderMaker=hexToByteArray(numberToHex(int(order['maker'],16),64))
        orderMarket=hexToByteArray(numberToHex(int(order['market'],16),64))
        bluefin=bytearray("Bluefin", encoding="utf-8")

        buffer=orderPriceHex+orderQuantityHex+orderLeverageHex+orderSalt+orderExpiration+orderMaker+orderMarket+flags+bluefin
      ```

   3. We then get the sha256 of the buffer.hex()
   4. We then sign it and append '1' to it, specifying that we signed it using ed25519

3. For signing onboarding signer we follow a different approach.

   1. What is onboarding signer: When we are calling a Bluefin init function we sign a string using our private key and send it to bluefin exchange along with our public key, bluefin exchange verifies it and returns us a token.
   2. For signing it we first convert our message to bytes and then add [3,0,0, len(message)] to the start of our bytearray and then our message. if our message length is greater than 256 then it wont fit in a byte in this case we follow BCS methodology to send our message.

4. For signing cancel order, there are two ways.
   1. We first sign the order and send it to bluefin. Now we have the hash of the order. We first change our encode our hash to BCS format.
      ```python
        sigDict={}
        sigDict['orderHashes']=order_hash
        encodedMessage=self.encode_message(sigDict)
      ```
   2. Please have a look at signer.py to see the implementation or encode_message.
   3. Then we sign the encodedMessage and send the signature to bluefin for cancelling order
5. For signing cancel order second method.
   1. We sign the order and send it to bluefin, now imagine we do not have the hash of our order.
   2. We resign our order and get the hash and then we follow the similar approach as above. Please have a look at `7.cancelling_orders.py` in our examples file.

## A detailed Guide on Onboarding:

1. Basically as explained earlier when sign the onboarding url and send it to bluefin, bluefin returns us the TOKEN.
2. The change in this repo is following.
3. ```python
        # imagine msg="https://testnet.bluefin.io"
        msgDict={}
        msgDict['onboardingUrl']=msg
        msg=json.dumps(msgDict,separators=(',', ':'))
        # we first create a json something like this '{"onboardingURL":"https://testnet.bluefin.io"}

        # we then convert this json to a bytearray
        msg_bytearray=bytearray(msg.encode("utf-8"))
        intent=bytearray()
        #we then append [3,0,0,length of our json object] to our intent bytearray
        intent.extend([3,0,0, len(msg_bytearray)])
        intent=intent+msg_bytearray

        # we then take a blake2b hash of intent bytearray we created
        hash=hashlib.blake2b(intent,digest_size=32)
        #then we finally sign the hash
   ```
## Margin Bank:
1. When you insert money to margin bank we give it in BASE6 but when we see balance it is in base9.  internally the functions are implemented that way.
2. We expect you to give the arguments directly in DECIMALS.


## Making Direct Contract Calls:
1. for making contract calls. The one interacting with our contracts are implemented internally in `client.py`
2. we have exposed some generic functions through which you can make direct contract calls yourself
   1. `def rpc_unsafe_moveCall(url,params, function_name: str, function_library: str, userAddress ,packageId, gasBudget=100000000 ):`
   2. `def rpc_sui_executeTransactionBlock(url, txBytes, signature):`
   3. The first one is used to serialise the contract calls you are going to make. 
   4. for second one you need to sign the result of first call with your signer and then make call along with serialised call and signature.
   5. internally all our contract calls to packages uses these functions. for more information have a look at `rpc.py`
3. For making calls to SUI functions
   1. For that we have exposed `def rpc_call_sui_function(url, params, method="suix_getCoins"):`
   2. Here you can specify the params and the name of the sui function you are calling.
   3. internally we use these calls to get the chain balance, usdc coins.
