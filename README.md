# Firefly Client Library

[<img alt="Firefly logo" src="https://raw.githubusercontent.com/fireflyprotocol/firefly_exchange_client/main/res/banner.png" />](#)

<div align="center">

![GitHub Workflow Status (with branch)](https://img.shields.io/github/actions/workflow/status/fireflyprotocol/bluefin-client-python-sui/publish_to_pypi.yml)
[![pypi version](https://img.shields.io/pypi/v/bluefun_client_sui?logo=pypi)](https://pypi.org/project/bluefin_client_sui/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

</div>

Python Client for the Firefly Exchange API and Smart Contracts for SUI.
​

### Install

The package can be installed from [PyPi](https://pypi.org/project/bluefin-client-sui/) using pip:

```
pip install bluefin_client_sui
```

Alternatively, you could run:

```
pip install .
```

The package currently supports python `>=3.8`. Find complete documentation on the library at https://docs.firefly.exchange/.

### Getting Started

When initializing the client, users must accept [terms and conditions](https://firefly.exchange/terms-of-use) and define network object containing the following values:

```json
{
  "apiGateway": "https://dapi.api.sui-prod.bluefin.io",
  "socketURL": "wss://dapi.api.sui-prod.bluefin.io",
  "dmsURL": "https://dapi.api.sui-prod.bluefin.io",
  "webSocketURL": "wss://notifications.api.sui-prod.bluefin.io",
  "onboardingUrl": "https://trade.bluefin.io"
}
```

Users can import predefined networks from [constants](https://github.com/fireflyprotocol/bluefin-client-python-sui/blob/main/src/bluefin_client_sui/constants.py):

```python
from bluefin_client_sui import Networks
```

For testing purposes use `Networks[SUI_STAGING]` and for production please use `Networks[SUI_PROD]`.

## Initialization example​

```python
from config import TEST_ACCT_KEY, TEST_NETWORK
from bluefin_client_sui import FireflyClient, Networks
from pprint import pprint
import asyncio

async def main():
  # initialize client
  client = FireflyClient(
      True, # agree to terms and conditions
      Networks[TEST_NETWORK], # network to connect with
      TEST_ACCT_KEY, # private key of wallet
      )

  # initialize the client
  # on boards user on firefly. Must be set to true for first time use
  await client.init(True)

  print('Account Address:', client.get_public_address())

  # # gets user account data on-chain
  data = await client.get_user_account_data()

  # close aio http connection
  await client.apis.close_session()

  pprint(data)

if __name__ == "__main__":
  loop = asyncio.new_event_loop()
  loop.run_until_complete(main())
  loop.close()
```

**Read-only Initialization:**
Firefly-client can also be initialized in `read-only` mode, below is the example:

```python
from config import TEST_ACCT_KEY, TEST_NETWORK
from bluefin_client_sui import FireflyClient, Networks
from pprint import pprint
import asyncio

async def main():
  # initialize client without providing private_key
  client = FireflyClient(
      True, # agree to terms and conditions
      Networks[TEST_NETWORK], # network to connect with
      )

  # Initializing client for the private key provided. The second argument api_token is optional
  await client.init(True,"54b0bfafc9a48728f76e52848a716e96d490263392e3959c2d44f05dea960761")

  # close aio http connection
  await client.apis.close_session()
  await client.dmsApi.close_session()

  pprint(data)

if __name__ == "__main__":
  loop = asyncio.new_event_loop()
  loop.run_until_complete(main())
  loop.close()
```

​Here is the [list](https://docs.bluefin.io/8/2.readonly-access-data) of APIs that can be accessed in `read-only` mode.

**Placing Orders:**

```python
from config import TEST_ACCT_KEY, TEST_NETWORK
from bluefin_client_sui import FireflyClient, Networks, MARKET_SYMBOLS, ORDER_SIDE, ORDER_TYPE, OrderSignatureRequest
import asyncio

async def main():
    # initialize client
    client = FireflyClient(
        True, # agree to terms and conditions
        Networks[TEST_NETWORK], # network to connect with
        TEST_ACCT_KEY, # private key of wallet
        )

    await client.init(True)

    user_leverage = await client.get_user_leverage(MARKET_SYMBOLS.ETH)

    # creates a LIMIT order to be signed
    signature_request = OrderSignatureRequest(
        symbol=MARKET_SYMBOLS.ETH,  # market symbol
        price=1900,  # price at which you want to place order
        quantity=0.01, # quantity
        side=ORDER_SIDE.SELL,
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

    await client.apis.close_session()


if __name__ == "__main__":
  loop = asyncio.new_event_loop()
  loop.run_until_complete(main())
  loop.close()
```

​
**Listening To Events Using Socket.io:**

```python
from config import TEST_ACCT_KEY, TEST_NETWORK
from bluefin_client_sui import FireflyClient, Networks, SOCKET_EVENTS
import asyncio
import time

def callback(event):
    print("Event data:", event)

async def main():
    # initialize
    client = FireflyClient(
        True, # agree to terms and conditions
        Networks[TEST_NETWORK], # network to connect with
        TEST_ACCT_KEY, # private key of wallet
        )
    await client.init(True)
    # make connection with firefly exchange
    await client.socket.open()

    # subscribe to local user events
    await client.socket.subscribe_user_update_by_token()

    # listen to exchange health updates and trigger callback
    await client.socket.listen(SOCKET_EVENTS.EXCHANGE_HEALTH.value, callback)
    time.sleep(10)
    # unsubscribe from user events
    await client.socket.unsubscribe_user_update_by_token()
    # close socket connection
    await client.socket.close()

if __name__ == "__main__":
  loop = asyncio.new_event_loop()
  loop.run_until_complete(main())
  loop.close()​
```

Look at the [example](https://github.com/fireflyprotocol/firefly_exchange_client/tree/main/examples) directory to see more examples on how to use this library.

**Listening To Events Using Web Sockets:**

```python
from config import TEST_ACCT_KEY, TEST_NETWORK
from bluefin_client_sui import FireflyClient, Networks, SOCKET_EVENTS, MARKET_SYMBOLS
import time
import asyncio

def callback(event):
    print("Event data:", event)

async def main():
    # initialize
    client = FireflyClient(
        True, # agree to terms and conditions
        Networks[TEST_NETWORK], # network to connect with
        TEST_ACCT_KEY, # private key of wallet
        )

    await client.init(True)

    def on_open(ws):
        # subscribe to global events
        resp = client.webSocketClient.subscribe_global_updates_by_symbol(symbol=MARKET_SYMBOLS.ETH)
        if resp:
            print("Subscribed to global updates")
        resp = client.webSocketClient.subscribe_user_update_by_token()
        if resp:
            print("Subscribed to user updates")

    # make connection with firefly exchange
    client.webSocketClient.initialize_socket(on_open=on_open)
    # listen to user order updates and trigger callback
    client.webSocketClient.listen(SOCKET_EVENTS.EXCHANGE_HEALTH.value, callback)

    time.sleep(60)

    # unsubscribe from global events
    client.webSocketClient.unsubscribe_global_updates_by_symbol(symbol=MARKET_SYMBOLS.ETH)
    client.webSocketClient.stop()


if __name__ == "__main__":
  loop = asyncio.new_event_loop()
  loop.run_until_complete(main())
  loop.close()
```
