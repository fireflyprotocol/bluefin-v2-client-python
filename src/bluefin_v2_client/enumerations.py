from enum import Enum


class ORDER_TYPE(Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP_MARKET = "STOP_MARKET"
    STOP_LIMIT = "STOP_LIMIT"


class ORDER_SIDE(Enum):
    BUY = "BUY"
    SELL = "SELL"


class MARKET_SYMBOLS(Enum):
    BTC = "BTC-PERP"
    ETH = "ETH-PERP"
    SOL = "SOL-PERP"
    SUI = "SUI-PERP"
    ARB = "ARB-PERP"
    APT = "APT-PERP"
    AVAX = "AVAX-PERP"
    TIA = "TIA-PERP"
    MATIC = "MATIC-PERP"
    SEI = "SEI-PERP"
    
class TIME_IN_FORCE(Enum):
    IMMEDIATE_OR_CANCEL = "IOC"
    GOOD_TILL_TIME = "GTT"


class ONBOARDING_MESSAGES(Enum):
    ONBOARDING = "Firefly Onboarding"
    KEY_DERIVATION = "Firefly Access Key"


class ORDER_STATUS(Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    PARTIAL_FILLED = "PARTIAL_FILLED"
    FILLED = "FILLED"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    STAND_BY = "STAND_BY"
    STAND_BY_PENDING = "STAND_BY_PENDING"


class CANCEL_REASON(Enum):
    UNDERCOLLATERALIZED = "UNDERCOLLATERALIZED"
    INSUFFICIENT_BALANCE = "INSUFFICIENT_BALANCE"
    USER_CANCELLED = "USER_CANCELLED"
    EXCEEDS_MARKET_BOUND = "EXCEEDS_MARKET_BOUND"
    COULD_NOT_FILL = "COULD_NOT_FILL"
    EXPIRED = "EXPIRED"
    USER_CANCELLED_ON_CHAIN = "USER_CANCELLED_ON_CHAIN"
    SYSTEM_CANCELLED = "SYSTEM_CANCELLED"
    SELF_TRADE = "SELF_TRADE"
    POST_ONLY_FAIL = "POST_ONLY_FAIL"
    FAILED = "FAILED"
    NETWORK_DOWN = "NETWORK_DOWN"


class Interval(Enum):
    _1m = "1m"
    _3m = "3m"
    _5m = "5m"
    _15m = "15m"
    _30m = "30m"
    _1h = "1h"
    _2h = "2h"
    _4h = "4h"
    _6h = "6h"
    _8h = "8h"
    _12h = "12h"
    _1d = "1d"
    _3d = "3d"
    _1w = "1w"
    _1M = "1M"


class SOCKET_EVENTS(Enum):
    GET_LAST_KLINE_WITH_INTERVAL = "{symbol}@kline@{interval}"
    # rooms that can be joined
    GLOBAL_UPDATES_ROOM = "globalUpdates"
    ORDERBOOK_DEPTH_STREAM_ROOM = "orderbookDepthStream"
    USER_UPDATES_ROOM = "userUpdates"
    # events that can be listened
    MARKET_DATA_UPDATE = "MarketDataUpdate"
    RECENT_TRADES = "RecentTrades"
    ORDERBOOK_UPDATE = "OrderbookUpdate"
    ORDERBOOK_DEPTH_UPDATES = "OrderbookDepthUpdate"
    ADJUST_MARGIN = "AdjustMargin"
    MARKET_HEALTH = "MarketHealth"
    EXCHANGE_HEALTH = "ExchangeHealth"
    ORDER_UPDATE = "OrderUpdate"
    ORDER_SENT_FOR_SETTLEMENT = "OrderSettlementUpdate"
    ORDER_REQUEUE_UPDATE = "OrderRequeueUpdate"
    ORDER_CANCELLED_ON_REVERSION_UPDATE = "OrderCancelledOnReversionUpdate"
    ORDER_CANCELLATION = "OrderCancelled"
    ORDER_CANCELLATION_FAILED = "OrderCancellationFailed"
    POSITION_UPDATE = "PositionUpdate"
    USER_TRADE = "UserTrade"
    USER_TRANSACTION = "UserTransaction"
    ACCOUNT_DATA = "AccountDataUpdate"


class MARGIN_TYPE(Enum):
    ISOLATED = "ISOLATED"
    CROSS = "CROSS"


class ADJUST_MARGIN(Enum):
    ADD = "ADD"
    REMOVE = "REMOVE"


class TRADE_TYPE(Enum):
    ISOLATED = "IsolatedTrader"
    LIQUIDATION = "IsolatedLiquidation"
