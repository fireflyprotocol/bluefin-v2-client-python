Networks = {
    "SUI_STAGING": {
        "url": "https://fullnode.testnet.sui.io:443",
        "apiGateway": "https://dapi.api.sui-staging.bluefin.io",
        "socketURL": "wss://dapi.api.sui-staging.bluefin.io",
        "dmsURL": "https://api.sui-staging.bluefin.io/dead-man-switch",
        "webSocketURL": "wss://notifications.api.sui-staging.bluefin.io",
        "onboardingUrl": "https://testnet.bluefin.io",
        "UUID": ""
    },
    "SUI_PROD": {
        "url": "https://fullnode.testnet.sui.io:443",
        "apiGateway": "https://dapi.api.sui-prod.bluefin.io",
        "socketURL": "wss://dapi.api.sui-prod.bluefin.io",
        "dmsURL": "https://api.sui-prod.bluefin.io/dead-man-switch",
        "webSocketURL": "wss://notifications.api.sui-prod.bluefin.io",
        "onboardingUrl": "https://trade-sui.bluefin.exchange",
        "UUID": ""
    },
    "SUI_PROD_INTERNAL": {
        "url": "https://fullnode.testnet.sui.io:443",
        "apiGateway": "https://dapi.api.sui-prod.int.bluefin.io",
        "socketURL": "wss://dapi.api.sui-prod.int.bluefin.io",
        "dmsURL": "https://api.sui-prod.int.bluefin.io/dead-man-switch",
        "webSocketURL": "wss://notifications.api.sui-prod.int.bluefin.io",
        "onboardingUrl": "https://trade-sui.bluefin.exchange",
        "UUID": ""
    },
}

ORDER_FLAGS = {"IS_BUY": 1, "IS_DECREASE_ONLY": 2}

TIME = {
    "SECONDS_IN_A_MINUTE": 60,
    "SECONDS_IN_A_DAY": 86400,
    "SECONDS_IN_A_MONTH": 2592000,
}

ADDRESSES = {
    "ZERO": "0x0000000000000000000000000000000000000000",
}

SERVICE_URLS = {
    "MARKET": {
        "ORDER_BOOK": "/orderbook",
        "RECENT_TRADE": "/recentTrades",
        "CANDLE_STICK_DATA": "/candlestickData",
        "EXCHANGE_INFO": "/exchangeInfo",
        "MARKET_DATA": "/marketData",
        "META": "/meta",
        "STATUS": "/status",
        "SYMBOLS": "/marketData/symbols",
        "CONTRACT_ADDRESSES": "/marketData/contractAddresses",
        "TICKER": "/ticker",
        "MASTER_INFO": "/masterInfo",
        "FUNDING_RATE": "/fundingRate",
    },
    "USER": {
        "USER_POSITIONS": "/userPosition",
        "USER_TRADES": "/userTrades",
        "ORDERS": "/orders",
        "GENERATE_READONLY_TOKEN": "/generateReadOnlyToken",
        "ACCOUNT": "/account",
        "USER_TRANSACTION_HISTORY": "/userTransactionHistory",
        "AUTHORIZE": "/authorize",
        "ADJUST_LEVERAGE": "/account/adjustLeverage",
        "FUND_GAS": "/account/fundGas",
        "TRANSFER_HISTORY": "/userTransferHistory",
        "FUNDING_HISTORY": "/userFundingHistory",
        "CANCEL_ON_DISCONNECT": "/dms-countdown",
    },
    "ORDERS": {
        "ORDERS": "/orders",
        "ORDERS_HASH": "/orders/hash",
    },
}
