from typing import TypedDict, List
from .enumerations import *


class Order(TypedDict):
    market: str
    price: int
    isBuy: bool
    reduceOnly: bool
    quantity: int
    postOnly: bool
    cancelOnRevert: bool
    orderbookOnly: bool
    leverage: int
    expiration: int
    salt: int
    maker: str
    ioc: bool


class SignedOrder(Order):
    typedSignature: str


class RequiredOrderFields(TypedDict):
    symbol: MARKET_SYMBOLS  # market for which to create order
    price: int  # price at which to place order. Will be zero for a market order
    quantity: int  # quantity/size of order
    side: ORDER_SIDE  # BUY/SELL
    orderType: ORDER_TYPE  # MARKET/LIMIT


class OrderSignatureRequest(RequiredOrderFields):
    leverage: int  # (optional) leverage to take, default is 1
    reduceOnly: bool  # (optional) Reduce Only feature is deprecated until further notice. Default is set to false.
    salt: int  # (optional)  random number for uniqueness of order. Generated randomly if not provided
    expiration: int  # (optional) time at which order will expire. Will be set to 1 month if not provided
    maker: str  # (optional) maker of the order, if not provided the account used to initialize the client will be default maker
    # isBuy: bool
    postOnly: bool
    cancelOnRevert: bool
    orderBookOnly: bool
    # deprecated
    ioc: bool
    timeInForce: TIME_IN_FORCE

    # for stop orders
    triggerPrice: float


class OrderSignatureResponse(RequiredOrderFields):
    maker: str
    orderSignature: str


class PlaceOrderRequest(OrderSignatureResponse):
    timeInForce: TIME_IN_FORCE  # IOC/GTT by default all orders are GTT
    postOnly: bool  # true/false, default is true
    cancelOnRevert: bool  # if true, the order will be cancelled in case of on-chain settlement error, default is false
    clientId: str  # id of the client


class GetOrderbookRequest(TypedDict):
    symbol: MARKET_SYMBOLS
    limit: int  # number of bids/asks to retrieve, should be <= 50


class OnboardingMessage(TypedDict):
    action: str
    onlySignOn: str


class OrderResponse(TypedDict):
    id: int
    clientId: str
    requestTime: int
    cancelReason: CANCEL_REASON
    orderStatus: ORDER_STATUS
    hash: str
    symbol: MARKET_SYMBOLS
    orderType: ORDER_TYPE
    timeInForce: TIME_IN_FORCE
    userAddress: str
    side: ORDER_SIDE
    price: str
    quantity: str
    leverage: str
    reduceOnly: bool
    expiration: int
    salt: int
    orderSignature: str
    filledQty: str
    avgFillPrice: str
    createdAt: int
    updatedAt: int
    makerFee: str
    takerFee: str
    openQty: str
    cancelOnRevert: bool


class GetOrderResponse(OrderResponse):
    fee: str
    postOnly: bool
    cancelOnRevert: bool
    triggerPrice: str


class GetCandleStickRequest(TypedDict):
    symbol: MARKET_SYMBOLS
    interval: Interval
    startTime: float
    endTime: float
    limit: int


class GetMarketRecentTradesRequest(TypedDict):
    symbol: MARKET_SYMBOLS
    pageSize: int
    pageNumber: int
    traders: TRADE_TYPE


class OrderCancelSignatureRequest(TypedDict):
    symbol: MARKET_SYMBOLS
    hashes: list
    parentAddress: str  # (optional) should only be provided by a sub account


class OrderCancellationRequest(OrderCancelSignatureRequest):
    signature: str


class CancelOrder(TypedDict):
    hash: str
    reason: str


class CancelOrderResponse(TypedDict):
    message: str
    data: dict


class GetTransactionHistoryRequest(TypedDict):
    symbol: MARKET_SYMBOLS  # will fetch orders of provided market
    pageSize: int  # will get only provided number of orders must be <= 50
    pageNumber: int  # will fetch particular page records. A single page contains 50 records.


class GetPositionRequest(GetTransactionHistoryRequest):
    parentAddress: str  # (optional) should be provided by sub accounts


class GetUserTradesRequest(TypedDict):
    symbol: MARKET_SYMBOLS
    maker: bool
    fromId: int
    startTime: int
    endTime: int
    pageSize: int
    pageNumber: int
    type: ORDER_TYPE
    parentAddress: str  # (optional) should be provided by sub account


class GetUserTradesHistoryRequest(TypedDict):
    symbol: MARKET_SYMBOLS
    maker: bool
    fromId: int
    startTime: int
    endTime: int
    limit: int
    cursor: int
    type: ORDER_TYPE
    parentAddress: str  # (optional) should be provided by sub account


class GetOrderRequest(GetTransactionHistoryRequest):
    statuses: List[ORDER_STATUS]  # (optional) status of orders to be fetched
    orderId: int  # (optional) the id of order to be fetched
    orderType: List[ORDER_TYPE]  # (optional) type of order Limit/Market
    orderHashes: List[str]  # (optional) hashes of order to be fetched
    parentAddress: str  # (optional) should be provided by sub accounts


class GetFundingHistoryRequest(TypedDict):
    symbol: MARKET_SYMBOLS  # will fetch orders of provided market
    pageSize: int  # will get only provided number of orders must be <= 50
    cursor: int  # will fetch particular page records. A single page contains 50 records.
    parentAddress: str  # (optional) should be provided by a sub account


class FundingHistoryResponse(TypedDict):
    id: int  # unique id
    symbol: MARKET_SYMBOLS  # market for which to create order
    userAddress: str  # user public address
    quantity: int  # size of position
    time: int  # created time
    appliedFundingRate: str  # funding rate percent applied
    isFundingRatePositive: bool  # was funding rate +ve or -ve
    payment: str  # amount
    isPaymentPositive: bool  # whether payment was deducted or added
    oraclePrice: str  # price from oracle
    side: ORDER_SIDE  # BUY/SELL
    blockNumber: int  # transaction block number
    isPositionPositive: bool  # is position LONG or SHORT


class GetFundingHistoryResponse(TypedDict):
    isMoreDataAvailable: bool  # boolean indicating if there is more data available
    nextCursor: int  # next page number
    data: List[FundingHistoryResponse]


class GetTransferHistoryRequest(TypedDict):
    pageSize: int  # will get only provided number of orders must be <= 50
    cursor: int  # will fetch particular page records. A single page contains 50 records.
    action: str  # (optional) Deposit / Withdraw


class UserTransferHistoryResponse(TypedDict):
    id: int  # unique id
    status: str  # status of transaction
    action: str  # Deposit / Withdraw
    amount: str  # amount withdrawn/deposited
    userAddress: str  # user public address
    blockNumber: int  # transaction block number
    latestTxHash: str  # transaction hash
    time: int  # created time
    createdAt: int
    updatedAt: int


class GetUserTransferHistoryResponse(TypedDict):
    isMoreDataAvailable: bool  # boolean indicating if there is more data available
    nextCursor: int  # next page number
    data: List[UserTransferHistoryResponse]


class CountDown(TypedDict):
    symbol: str
    countDown: int


class GetCancelOnDisconnectTimerRequest(TypedDict):
    symbol: MARKET_SYMBOLS  # will fetch Cancel On Disconnect Timer of provided market
    parentAddress: str  # (optional) should be provided by a sub account


class PostTimerAttributes(TypedDict):
    countDowns: List[CountDown]
    parentAddress: str


class FailedCountDownResetResponse(TypedDict):
    symbol: str
    reason: str


class PostTimerResponse(TypedDict):
    acceptedToReset: List[str]
    failedReset: List[FailedCountDownResetResponse]


class GenerateReferralCodeRequest(TypedDict):
  referralCode: str
  campaignId: int

class GenerateReferralCodeResponse(TypedDict):
  referralAddress: str
  referralCode: str
  message: str

class LinkReferredUserRequest(TypedDict):
    referralCode: str

class LinkReferredUserResponse(TypedDict):
  referralCode: str
  refereeAddress: str
  campaignId: int
  message: str

class GetReferrerInfoResponse(TypedDict):
  isReferee: bool


class CampaignDetailsConfig(TypedDict):
  cashShare: str
  tokenShare: str
  shareOfFees: str
  refereeDiscount: str

class GetCampaignDetailsResponse(TypedDict):
  id: str
  campaignName: str
  parentCampaignName: str
  startDate: str
  endDate: str
  isActive: bool
  epochDurationSeconds: int
  config: CampaignDetailsConfig
  createdAt: str
  updatedAt: str

class GetCampaignRewardsResponse(TypedDict):
  campaignName: str
  campaignConfig: CampaignDetailsConfig
  cashReward: str
  tokenReward: str

class GetAffiliatePayoutsResponse(TypedDict):
  epStartDate: str
  epEndDate: str
  isActive: bool
  totalReferralFees: str
  cashReward: str
  tokenReward: str
  epochNumber: str

class GetAffiliateRefereeDetailsRequest(TypedDict):
  campaignId: int
  pageNumber: int
  pageSize: int
  parentAddress: str 
class AffiliateRefereeDetailsData(TypedDict):
  userAddress: str
  lastTraded: str
  dateJoined: str
  feesPaid: str

class GetAffiliateRefereeDetailsResponse(TypedDict):
  data: List[AffiliateRefereeDetailsData]
  nextCursor: int
  isMoreDataAvailable: bool


class GetAffiliateRefereeCountResponse(TypedDict):
  referralCode: str
  referralCount: int


class GetUserRewardsHistoryRequest(TypedDict):
  pageSize: int
  cursor: int
  parentAddress: str 

class UserRewardsHistoryData(TypedDict):
  programName: str
  parentProgramName: str
  startDate: str
  endDate: str
  cashReward: str
  tokenReward: str
  isActive: bool
  cursor: str
  epochNumber: str

class GetUserRewardsHistoryResponse(TypedDict):
  data: List[UserRewardsHistoryData]
  nextCursor: int
  isMoreDataAvailable: bool

class RewardsSummaryData(TypedDict):
  campaignName: str
  totalCashReward: str
  totalTokenReward: str

class GetUserRewardsSummaryResponse(TypedDict):
  totalTokenReward: str
  totalCashReward: str
  campaignData: List[RewardsSummaryData]

class GetTradeAndEarnRewardsOverviewResponse(TypedDict):
  totalHistoricalRewards: str
  totalActiveRewards: str
  totalFeePaid: str
  latestEpochNumber: str
  latestEpochStart: int
  latestEpochEnd: int
  latestEpochTotalFee: str
  latestEpochTotalRewards: str


class GetTradeAndEarnRewardsDetailRequest(TypedDict):
  campaignId: int
  pageSize: int
  cursor: int
  parentAddress: str 

class TradeAndEarnRewardsDetailData(TypedDict):
  tradingRewards: str
  feePaid: str
  cursor: str
  id: int
  isActive: bool
  startDate: str
  endDate: str
  epochNumber: str

class GetTradeAndEarnRewardsDetailResponse(TypedDict):
  data: List[TradeAndEarnRewardsDetailData]
  nextCursor: str
  isMoreDataAvailable: bool

class GetTotalHistoricalTradingRewardsResponse(TypedDict):
  totalTokenRewards: str

class GetMakerRewardsSummaryResponse(TypedDict):
  latestEpochStart: int
  latestEpochEnd: int
  latestEpochNumber: str
  latestEpochTotalRewards: str
  totalActiveRewards: str
  totalHistoricalRewards: str

class GetMakerRewardDetailsRequest(TypedDict):
  symbol: str
  pageSize: int
  cursor: int
  parentAddress: str 




class MakerRewardDetailsData(TypedDict):
    latestEpochNumber: str
    status: str
    makerVolume: str
    volumePercentage: str
    rewardPoolPercentage: str
    makerRewards: str
    startDate: str
    endDate: str
    cursor: str
    liquidityScore: str  # come if symbol provided in request
    uptimePercentage: str  # come if symbol provided in request


class GetMakerRewardDetailsResponse(TypedDict):
    data: List[MakerRewardDetailsData]
    nextCursor: int
    isMoreDataAvailable: bool


class GetUserWhiteListStatusForMarkeMakerResponse(TypedDict):
  isWhitelist: bool


class CursorPaginationPayload(TypedDict):
  pageSize: int  # will get only provided number of orders must be <= 50
  cursor: int 
