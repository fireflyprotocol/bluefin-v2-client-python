import unittest
import json
import os
import sys
import pytest

sys.path.insert(1, os.path.join(os.getcwd(), "src"))
sys.path.insert(1, os.path.join(os.getcwd(), "tests"))

from bluefin_v2_client import BluefinClient, Networks
from bluefin_v2_client import (
    BluefinClient,
    Networks,
    MARKET_SYMBOLS,
    ORDER_SIDE,
    ORDER_TYPE,
    OrderSignatureRequest,
)
import time

TEST_ACCT_KEY = (
    "negative repeat fold noodle symptom spirit spend trophy merge ethics math erupt"
)
TEST_NETWORK = "SUI_STAGING"


@pytest.mark.asyncio
async def test_place_orders():
    client = BluefinClient(
        True,  # agree to terms and conditions
        Networks[TEST_NETWORK],  # network to connect with
        TEST_ACCT_KEY,  # seed phrase of the wallet
    )
    # Initializing client for the private key provided. The second argument api_token is optional
    await client.init(True)
    # default leverage of account is set to 3 on Bluefin
    user_leverage = await client.get_user_leverage(MARKET_SYMBOLS.ETH)
    print("User Default Leverage", user_leverage)

    # Sign and place a limit order at 4x leverage. Order is signed using the account seed phrase set on the client
    adjusted_leverage = 4
    await client.adjust_leverage(MARKET_SYMBOLS.ETH, adjusted_leverage)
    signature_request = OrderSignatureRequest(
        symbol=MARKET_SYMBOLS.ETH,  # market symbol
        price=1770.2,  # price at which you want to place order
        quantity=0.02,  # quantity
        side=ORDER_SIDE.BUY,
        orderType=ORDER_TYPE.LIMIT,
        leverage=adjusted_leverage,
        expiration=int(
            (time.time() + 864000) * 1000
        ),  # expiry after 10 days, default expiry is a month
    )
    signed_order = client.create_signed_order(signature_request)
    resp = await client.post_signed_order(signed_order)
    assert resp["orderStatus"] == "PENDING"


@pytest.mark.asyncio
async def test_placeOrderLev2():
    client = BluefinClient(
        True,  # agree to terms and conditions
        Networks[TEST_NETWORK],  # network to connect with
        TEST_ACCT_KEY,  # seed phrase of the wallet
    )
    # Initializing client for the private key provided. The second argument api_token is optional
    await client.init(True)
    # sign and place a market order at 2x leverage
    adjusted_leverage = 2
    await client.adjust_leverage(MARKET_SYMBOLS.BTC, adjusted_leverage)
    signature_request = OrderSignatureRequest(
        symbol=MARKET_SYMBOLS.BTC,
        price=0,
        quantity=0.01,
        leverage=adjusted_leverage,
        side=ORDER_SIDE.BUY,
        reduceOnly=False,
        postOnly=False,
        orderbookOnly=True,
        orderType=ORDER_TYPE.MARKET,
    )
    signed_order = client.create_signed_order(signature_request)
    resp = await client.post_signed_order(signed_order)
    assert resp["orderStatus"] == "PENDING"
