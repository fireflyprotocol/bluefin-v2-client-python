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
        "url": "https://fullnode.mainnet.sui.io:443",
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

SUI_CLOCK_OBJECT_ID = "0x0000000000000000000000000000000000000000000000000000000000000006"

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
        "USER_TRADES_HISTORY": "/userTradesHistory",
    },
    "GROWTH": {
    "REFERRER_INFO": "/growth/getReferrerInfo",
    "CAMPAIGN_DETAILS": "/growth/campaignDetails",
    "CAMPAIGN_REWARDS": "/growth/campaignRewards",
    "AFFILIATE_PAYOUTS": "/growth/affiliate/payouts",
    "AFFILIATE_REFEREE_DETAILS": "/growth/affiliate/refereeDetails",
    "AFFILIATE_REFEREES_COUNT": "/growth/refereesCount",
    "USER_REWARDS_HISTORY": "/growth/userRewards/history",
    "USER_REWARDS_SUMMARY": "/growth/userRewards/summary",
    "REWARDS_OVERVIEW": "/growth/tradeAndEarn/rewardsOverview",
    "REWARDS_DETAILS": "/growth/tradeAndEarn/rewardsDetail",
    "TOTAL_HISTORICAL_TRADING_REWARDS":
      "/growth/tradeAndEarn/totalHistoricalTradingRewards",
    "MAKER_REWARDS_SUMMARY": "/growth/marketMaker/maker-rewards-summary",
    "MAKER_REWARDS_DETAILS": "/growth/marketMaker/maker-rewards-detail",
    "MAKER_WHITELIST_STATUS": "/growth/marketMaker/whitelist-status",
    "GENERATE_CODE": "/growth/generateCode",
    "AFFILIATE_LINK_REFERRED_USER": "/growth/affiliate/linkReferee",
    "OPEN_REFERRAL_REFEREE_DETAILS": "/growth/openReferral/refereeDetails",
    "OPEN_REFERRAL_PAYOUTS": "/growth/openReferral/payoutsHistory",
    "OPEN_REFERRAL_GENERATE_CODE": "/growth/generateAutoReferralCode",
    "OPEN_REFERRAL_LINK_REFERRED_USER": "growth/openReferral/linkReferee",
    "OPEN_REFERRAL_OVERVIEW": "/growth/openReferral/rewardsOverview",
    "OPEN_REFERRAL_REFEREES_COUNT": "/growth/refereesCount",
    },
    "ORDERS": {
        "ORDERS": "/orders",
        "ORDERS_HASH": "/orders/hash",
    },
}
