import json
from copy import deepcopy

from .api_service import APIService
from .contracts import Contracts
from .order_signer import OrderSigner
from .onboarding_signer import OnboardingSigner
from .constants import TIME, SERVICE_URLS
from .sockets_lib import Sockets
from .websocket_client import WebsocketClient
from .signer import Signer
from .utilities import *
from .rpc import *
from .account import *
from .interfaces import *
from .enumerations import *

DEAULT_EXCHANGE_LEVERAGE = 3


class BluefinClient:
    """
    A class to represent a client for interacting with bluefin offchain and onchain APIs.
    """

    def __init__(self, are_terms_accepted, network, private_key=""):
        self.are_terms_accepted = are_terms_accepted
        self.network = network
        if private_key != "":
            # currently we only support seed phrase
            self.account = SuiWallet(seed=private_key)
            # self.account = Account.from_key(private_key)
        self.apis = APIService(
            self.network["apiGateway"], default_value(self.network, "UUID", "")
        )
        self.dms_api = APIService(self.network["dmsURL"])
        self.socket = Sockets(self.network["socketURL"])
        self.ws_client = WebsocketClient(self.network["webSocketURL"])
        self.contracts = Contracts()
        self.order_signer = OrderSigner()
        self.onboarding_signer = OnboardingSigner()
        self.contract_signer = Signer()
        self.url = self.network["url"]

    async def init(self, user_onboarding=True, api_token=""):
        """
        Initialize the client.
        Inputs:
            user_onboarding (bool, optional): If set to true onboards the user address to exchange and gets authToken. Defaults to True.
            api_token(string, optional): API token to initialize client in read-only mode
        """
        contract_info = await self.get_contract_addresses()
        self.contracts.set_contract_addresses(contract_info)

        if api_token:
            self.apis.api_token = api_token
            # for socket
            self.socket.set_api_token(api_token)
            self.ws_client.set_api_token(api_token)
        # In case of api_token received, user onboarding is not done
        elif user_onboarding:
            self.apis.auth_token = await self.onboard_user()
            self.dms_api.auth_token = self.apis.auth_token
            self.socket.set_token(self.apis.auth_token)
            self.ws_client.set_token(self.apis.auth_token)

    async def onboard_user(self, token: str = None):
        """
        On boards the user address and returns user authentication token.
        Inputs:
            token: user access token, if you possess one.
        Returns:
            str: user authorization token
        """
        user_auth_token = token

        # if no auth token provided create on
        if not user_auth_token:
            onboarding_signature = self.onboarding_signer.create_signature(
                self.network["onboardingUrl"], self.account.privateKeyBytes
            )
            onboarding_signature = (
                onboarding_signature + self.account.publicKeyBase64.decode()
            )
            response = await self.authorize_signed_hash(onboarding_signature)

            if "error" in response:
                raise SystemError(
                    f"Authorization error: {response['error']['message']}"
                )

            user_auth_token = response["token"]

        return user_auth_token


    def set_uuid(self, uuid):
        self.apis.set_uuid(uuid)
        self.dms_api.set_uuid(uuid)


    async def authorize_signed_hash(self, signed_hash: str):
        """
        Registers user as an authorized user on server and returns authorization token.
        Inputs:
            signed_hash: signed onboarding hash
        Returns:
            dict: response from user authorization API Bluefin
        """
        return await self.apis.post(
            SERVICE_URLS["USER"]["AUTHORIZE"],
            {
                "signature": signed_hash,
                "userAddress": self.account.address,
                "isTermAccepted": self.are_terms_accepted,
            },
        )

    def create_order_to_sign(self, params: OrderSignatureRequest) -> Order:
        """
        Creates order signature request for an order.
        Inputs:
            params (OrderSignatureRequest): parameters to create order with, refer OrderSignatureRequest

        Returns:
            Order: order raw info
        """
        expiration = current_unix_timestamp()
        # MARKET ORDER set expiration of 1 minute
        if params["orderType"] == ORDER_TYPE.MARKET:
            expiration += TIME["SECONDS_IN_A_MINUTE"]
            expiration *= 1000
        # LIMIT ORDER set expiration of 30 days
        else:
            expiration += TIME["SECONDS_IN_A_MONTH"]
            expiration *= 1000

        return Order(
            market=default_value(
                params, "market", self.contracts.get_perpetual_id(params["symbol"])
            ),
            isBuy=params["side"] == ORDER_SIDE.BUY,
            price=params["price"],
            quantity=params["quantity"],
            leverage=default_value(params, "leverage", 1),
            maker=params["maker"].lower()
            if "maker" in params
            else self.account.address.lower(),
            reduceOnly=default_value(params, "reduceOnly", False),
            postOnly=default_value(params, "postOnly", False),
            orderbookOnly=default_value(params, "orderbookOnly", True),
            expiration=default_value(params, "expiration", expiration),
            salt=default_value(params, "salt", random_number(1000000)),
            ioc=default_value(params, "ioc", False),
        )

    def create_signed_order(self, req: OrderSignatureRequest) -> OrderSignatureResponse:
        """
        Create an order from provided params and signs it using the private key of the account
        Inputs:
            params (OrderSignatureRequest): parameters to create order with
        Returns:
            OrderSignatureResponse: order raw info and generated signature
        """
        sui_params = deepcopy(req)
        sui_params["price"] = to1e18(req["price"])
        sui_params["quantity"] = to1e18(req["quantity"])
        sui_params["leverage"] = to1e18(req["leverage"])

        order = self.create_order_to_sign(sui_params)
        symbol = sui_params["symbol"].value
        order_signature = self.order_signer.sign_order(
            order, self.account.privateKeyBytes
        )
        order_signature = order_signature + self.account.publicKeyBase64.decode()
        return OrderSignatureResponse(
            symbol=symbol,
            price=sui_params["price"],
            quantity=sui_params["quantity"],
            side=sui_params["side"],
            leverage=sui_params["leverage"],
            reduceOnly=default_value(sui_params, "reduceOnly", False),
            salt=order["salt"],
            expiration=order["expiration"],
            orderSignature=order_signature,
            orderType=sui_params["orderType"],
            maker=order["maker"],
            orderbookOnly=default_value(sui_params, "orderbookOnly", True),
        )

    def create_signed_cancel_order(
        self, params: OrderSignatureRequest, parentAddress: str = ""
    ):
        """
            Creates a cancel order request from provided params and signs it using the private
            key of the account

        Inputs:
            params (OrderSignatureRequest): parameters to create cancel order with
            parentAddress (str): Only provided by a sub account

        Returns:
            OrderSignatureResponse: generated cancel signature
        """
        sui_params = deepcopy(params)
        sui_params["price"] = to1e18(params["price"])
        sui_params["quantity"] = to1e18(params["quantity"])
        sui_params["leverage"] = to1e18(params["leverage"])

        order_to_sign = self.create_order_to_sign(sui_params)
        hash_val = self.order_signer.get_order_hash(order_to_sign, withBufferHex=False)
        return self.create_signed_cancel_orders(
            params["symbol"], hash_val.hex(), parentAddress
        )

    def create_signed_cancel_orders(
        self, symbol: MARKET_SYMBOLS, order_hash: list, parentAddress: str = ""
    ):
        """
            Creates a cancel order from provided params and sign it using the private
            key of the account

        Inputs:
            params (list): a list of order hashes
            parentAddress (str): only provided by a sub account
        Returns:
            OrderCancellationRequest: containing symbol, hashes and signature
        """
        if isinstance(order_hash, list) is False:
            order_hash = [order_hash]
        cancel_hash = self.order_signer.encode_message({"orderHashes": order_hash})
        hash_sig = (
            self.order_signer.sign_hash(cancel_hash, self.account.privateKeyBytes, "")
            + self.account.publicKeyBase64.decode()
        )
        return OrderCancellationRequest(
            symbol=symbol.value,
            hashes=order_hash,
            signature=hash_sig,
            parentAddress=parentAddress,
        )

    async def post_cancel_order(self, params: OrderCancellationRequest):
        """
        POST cancel order request to Bluefin
        Inputs:
            params(dict): a dictionary with OrderCancellationRequest required params
        Returns:
            dict: response from orders delete API Bluefin
        """

        return await self.apis.delete(
            SERVICE_URLS["ORDERS"]["ORDERS_HASH"],
            {
                "symbol": params["symbol"],
                "orderHashes": params["hashes"],
                "cancelSignature": params["signature"],
                "parentAddress": params["parentAddress"],
            },
            auth_required=True,
        )

    async def cancel_all_orders(
        self,
        symbol: MARKET_SYMBOLS,
        status: List[ORDER_STATUS],
        parentAddress: str = "",
    ):
        """
        GETs all orders of specified status for the specified symbol,
        and creates a cancellation request for all orders and
        POSTs the cancel order request to Bluefin
        Inputs:
            symbol (MARKET_SYMBOLS): Market for which orders are to be cancelled
            status (List[ORDER_STATUS]): status of orders that need to be cancelled
            parentAddress (str): address of parent account, only provided by sub account
        Returns:
            dict: response from orders delete API Bluefin
        """
        orders = await self.get_orders(
            {"symbol": symbol, "parentAddress": parentAddress, "statuses": status}
        )

        hashes = []
        for i in orders:
            hashes.append(i["hash"])

        if len(hashes) > 0:
            req = self.create_signed_cancel_orders(symbol, hashes, parentAddress)
            return await self.post_cancel_order(req)

        return False

    async def post_signed_order(self, params: PlaceOrderRequest):
        """
        Creates an order from provided params and signs it using the private
        key of the account

        Inputs:
            params (OrderSignatureRequest): parameters to create order with

        Returns:
            OrderSignatureResponse: order raw info and generated signature
        """

        return await self.apis.post(
            SERVICE_URLS["ORDERS"]["ORDERS"],
            {
                "orderbookOnly": params["orderbookOnly"],
                "symbol": params["symbol"],
                "price": params["price"],
                "quantity": params["quantity"],
                "leverage": params["leverage"],
                "userAddress": params["maker"],
                "orderType": params["orderType"].value,
                "side": params["side"].value,
                "reduceOnly": params["reduceOnly"],
                "salt": params["salt"],
                "expiration": params["expiration"],
                "orderSignature": params["orderSignature"],
                "timeInForce": default_enum_value(
                    params, "timeInForce", TIME_IN_FORCE.GOOD_TILL_TIME
                ),
                "postOnly": default_value(params, "postOnly", False),
                "cancelOnRevert": default_value(params, "cancelOnRevert", False),
                "clientId": "bluefin-v2-client-python: {}".format(
                    default_value(params, "clientId", "bluefin-python-client")
                ),
            },
            auth_required=True,
        )

    ## Contract calls
    async def deposit_margin_to_bank(self, amount: int, coin_id: str = "") -> bool:
        """
        Deposits given amount of USDC from user's account to margin bank

        Inputs:
            amount (number): quantity of usdc to be deposited to bank in base decimals (1,2 etc)
            coin_id (string) (optional): the id of the coin you want the amount to be deducted from
        Returns:
            Boolean: true if amount is successfully deposited, false otherwise
        """
        if coin_id == "":
            coin_id = await self._get_coin_having_balance(amount)
        package_id = self.contracts.get_package_id()
        user_address = self.account.getUserAddress()
        callArgs = []
        callArgs.append(self.contracts.get_bank_id())
        callArgs.append(self.account.getUserAddress())
        callArgs.append(str(toUsdcBase(amount)))
        callArgs.append(coin_id)
        txBytes = rpc_unsafe_moveCall(
            self.url,
            callArgs,
            "deposit_to_bank",
            "margin_bank",
            user_address,
            package_id,
        )
        signature = self.contract_signer.sign_tx(txBytes, self.account)
        res = rpc_sui_executeTransactionBlock(self.url, txBytes, signature)

        if res["result"]["effects"]["status"]["status"] == "success":
            return True
        else:
            return False

    async def withdraw_margin_from_bank(self, amount: Union[float, int]) -> bool:
        """
        Withdraws given amount of usdc from margin bank if possible

        Inputs:
            amount (number): quantity of usdc to be withdrawn from bank in base decimals (1,2 etc)

        Returns:
            Boolean: true if amount is successfully withdrawn, false otherwise
        """

        bank_id = self.contracts.get_bank_id()
        account_address = self.account.getUserAddress()

        callArgs = [
            bank_id,
            account_address,
            str(toUsdcBase(amount)),
        ]
        txBytes = rpc_unsafe_moveCall(
            self.url,
            callArgs,
            "withdraw_from_bank",
            "margin_bank",
            self.account.getUserAddress(),
            self.contracts.get_package_id(),
        )
        signature = self.contract_signer.sign_tx(txBytes, self.account)
        res = rpc_sui_executeTransactionBlock(self.url, txBytes, signature)

        if res["result"]["effects"]["status"]["status"] == "success":
            return True
        else:
            return False

    async def withdraw_all_margin_from_bank(self):
        """
        Withdraws everything of usdc from margin bank

        Inputs:
            No input Required
        Returns:
            Boolean: true if amount is successfully withdrawn, false otherwise
        """
        bank_id = self.contracts.get_bank_id()
        account_address = self.account.getUserAddress()

        callArgs = [bank_id, account_address]
        txBytes = rpc_unsafe_moveCall(
            self.url,
            callArgs,
            "withdraw_all_margin_from_bank",
            "margin_bank",
            self.account.getUserAddress(),
            self.contracts.get_package_id(),
        )
        signature = self.contract_signer.sign_tx(txBytes, self.account)
        res = rpc_sui_executeTransactionBlock(self.url, txBytes, signature)

        if res["result"]["effects"]["status"]["status"] == "success":
            return True
        else:
            return False

    async def adjust_leverage(self, symbol, leverage, parentAddress: str = ""):
        """
        Adjusts user leverage to the provided one for their current position on-chain and off-chain.
        If a user has no position for the provided symbol, leverage only recorded off-chain

        Inputs:
            symbol (MARKET_SYMBOLS): market for which to adjust user leverage
            leverage (number): new leverage to be set. Must be in base decimals (1,2 etc.)
            parentAddress (str): optional, if provided, the leverage of parent is
                                being adjusted (for sub accounts only)
        Returns:
            Boolean: true if the leverage is successfully adjusted
        """

        user_position = await self.get_user_position(
            {"symbol": symbol, "parentAddress": parentAddress}
        )

        account_address = self.account.address if parentAddress == "" else parentAddress
        # implies user has an open position on-chain, perform on-chain leverage update
        if user_position != {}:
            callArgs = []
            callArgs.append(self.contracts.get_perpetual_id(symbol))
            callArgs.append(self.contracts.get_bank_id())
            callArgs.append(self.contracts.get_sub_account_id())
            callArgs.append(account_address)
            callArgs.append(str(to1e18(leverage)))
            callArgs.append(self.contracts.get_price_oracle_object_id(symbol))
            txBytes = rpc_unsafe_moveCall(
                self.url,
                callArgs,
                "adjust_leverage",
                "exchange",
                self.account.getUserAddress(),
                self.contracts.get_package_id(),
            )
            signature = self.contract_signer.sign_tx(txBytes, self.account)
            result = rpc_sui_executeTransactionBlock(self.url, txBytes, signature)
            if result["result"]["effects"]["status"]["status"] == "success":
                return True
            else:
                return False

        res = await self.apis.post(
            SERVICE_URLS["USER"]["ADJUST_LEVERAGE"],
            {
                "symbol": symbol.value,
                "address": account_address,
                "leverage": to1e18(leverage),
                "marginType": MARGIN_TYPE.ISOLATED.value,
            },
            auth_required=True,
        )
        return res

    async def adjust_margin(
        self,
        symbol: MARKET_SYMBOLS,
        operation: ADJUST_MARGIN,
        amount: str,
        parentAddress: str = "",
    ):
        """
        Adjusts user's on-chain position by adding or removing the specified amount of margin.
        Performs on-chain contract call, the user must have gas tokens
        Inputs:
            symbol (MARKET_SYMBOLS): market for which to adjust user leverage
            operation (ADJUST_MARGIN): ADD/REMOVE adding or removing margin to position
            amount (number): amount of margin to be adjusted
            parentAddress (str): optional, if provided, the margin of parent is
                                being adjusted (for sub accounts only)
        Returns:
            Boolean: true if the margin is adjusted
        """

        user_position = await self.get_user_position(
            {"symbol": symbol, "parentAddress": parentAddress}
        )

        if user_position == {}:
            raise (Exception(f"User has no open position on market: {symbol}"))

        callArgs = []
        callArgs.append(self.contracts.get_perpetual_id(symbol))
        callArgs.append(self.contracts.get_bank_id())

        callArgs.append(self.contracts.get_sub_account_id())
        callArgs.append(self.account.getUserAddress())
        callArgs.append(str(to1e18(amount)))
        callArgs.append(self.contracts.get_price_oracle_object_id(symbol))
        if operation == ADJUST_MARGIN.ADD:
            txBytes = rpc_unsafe_moveCall(
                self.url,
                callArgs,
                "add_margin",
                "exchange",
                self.account.getUserAddress(),
                self.contracts.get_package_id(),
            )

        else:
            txBytes = rpc_unsafe_moveCall(
                self.url,
                callArgs,
                "remove_margin",
                "exchange",
                self.account.getUserAddress(),
                self.contracts.get_package_id(),
            )

        signature = self.contract_signer.sign_tx(txBytes, self.account)
        result = rpc_sui_executeTransactionBlock(self.url, txBytes, signature)
        if result["result"]["effects"]["status"]["status"] == "success":
            return True
        else:
            return False

    async def update_sub_account(self, sub_account_address: str, status: bool) -> bool:
        """
        Used to whitelist and account as a sub account or revoke sub account status from an account.
        Inputs:
            sub_account_address (str): address of the sub account
            status (bool): new status of the sub account

        Returns:
            Boolean: true if the sub account status is update
        """
        callArgs = []
        callArgs.append(self.contracts.get_sub_account_id())
        callArgs.append(sub_account_address)
        callArgs.append(status)
        txBytes = rpc_unsafe_moveCall(
            self.url,
            callArgs,
            "set_sub_account",
            "roles",
            self.account.getUserAddress(),
            self.contracts.get_package_id(),
        )

        signature = self.contract_signer.sign_tx(txBytes, self.account)
        result = rpc_sui_executeTransactionBlock(self.url, txBytes, signature)
        if result["result"]["effects"]["status"]["status"] == "success":
            return True
        else:
            return False

    async def get_native_chain_token_balance(self) -> float:
        """
        Returns user's native chain token (SUI) balance
        """
        try:
            callArgs = []
            callArgs.append(self.account.getUserAddress())
            callArgs.append("0x2::sui::SUI")

            result = rpc_call_sui_function(
                self.url, callArgs, method="suix_getBalance"
            )["totalBalance"]
            return fromSuiBase(result)
        except Exception as e:
            raise (Exception(f"Failed to get balance, error: {e}"))

    async def get_usdc_coins(self):
        """
        Returns the list of the usdc coins owned by user
        """
        try:
            callArgs = []
            callArgs.append(self.account.getUserAddress())
            callArgs.append(self.contracts.get_currency_type())
            result = rpc_call_sui_function(self.url, callArgs, method="suix_getCoins")
            return result
        except Exception as e:
            raise (Exception("Failed to get USDC coins, Exception: {}".format(e)))

    async def get_usdc_balance(self) -> float:
        """
        Returns user's USDC token balance on Bluefin.
        """
        try:
            callArgs = []
            callArgs.append(self.account.getUserAddress())
            callArgs.append(self.contracts.get_currency_type())
            result = rpc_call_sui_function(
                self.url, callArgs, method="suix_getBalance"
            )["totalBalance"]
            return fromUsdcBase(result)

        except Exception as e:
            raise (Exception("Failed to get balance, Exception: {}".format(e)))

    async def get_margin_bank_balance(self) -> float:
        """
        Returns user's Margin Bank balance.
        """
        try:
            call_args = []
            call_args.append(self.contracts.get_bank_table_id())
            call_args.append(
                {"type": "address", "value": self.account.getUserAddress()}
            )
            result = rpc_call_sui_function(
                self.url, call_args, method="suix_getDynamicFieldObject"
            )

            balance = fromSuiBase(
                result["data"]["content"]["fields"]["value"]["fields"]["balance"]
            )
            return balance
        except Exception as e:
            raise (Exception("Failed to get balance, Exception: {}".format(e)))

    ## Market endpoints
    async def get_orderbook(self, params: GetOrderbookRequest):
        """
        Returns a dictionary containing the orderbook snapshot.
        Inputs:
            params(GetOrderbookRequest): the order symbol and limit(orderbook depth)
        Returns:
            dict: Orderbook snapshot
        """
        params = extract_enums(params, ["symbol"])
        return await self.apis.get(SERVICE_URLS["MARKET"]["ORDER_BOOK"], params)

    async def get_exchange_status(self):
        """
        Returns a dictionary containing the exchange status.
        Returns:
            dict: exchange status
        """
        return await self.apis.get(SERVICE_URLS["MARKET"]["STATUS"], {})

    async def get_market_symbols(self):
        """
        Returns a list of active market symbols.
        Returns:
            list: active market symbols
        """
        return await self.apis.get(SERVICE_URLS["MARKET"]["SYMBOLS"], {})

    async def get_funding_rate(self, symbol: MARKET_SYMBOLS):
        """
        Returns a dictionary containing the current funding rate on market.
        Inputs:
            symbol(MARKET_SYMBOLS): symbol of market
        Returns:
            dict: Funding rate into
        """
        return await self.apis.get(
            SERVICE_URLS["MARKET"]["FUNDING_RATE"], {"symbol": symbol.value}
        )

    async def get_transfer_history(self, params: GetTransferHistoryRequest):
        """
        Returns a list of the user's transfer history records, a boolean indicating if there is/are more page(s),
            and the next page number
        Inputs:
            params(GetTransferHistoryRequest): params required to fetch transfer history
        Returns:
            GetUserTransferHistoryResponse:
                isMoreDataAvailable: boolean indicating if there is/are more page(s)
                nextCursor: the next page number
                data: a list of the user's transfer history record
        """

        return await self.apis.get(
            SERVICE_URLS["USER"]["TRANSFER_HISTORY"], params, auth_required=True
        )

    async def get_funding_history(self, params: GetFundingHistoryRequest):
        """
        Returns a list of the user's funding payments, a boolean indicating if there is/are more page(s),
            and the next page number
        Inputs:
            params(GetFundingHistoryRequest): params required to fetch funding history
        Returns:
            GetFundingHistoryResponse:
                isMoreDataAvailable: boolean indicating if there is/are more page(s)
                nextCursor: the next page number
                data: a list of the user's funding payments
        """

        params = extract_enums(params, ["symbol"])

        return await self.apis.get(
            SERVICE_URLS["USER"]["FUNDING_HISTORY"], params, auth_required=True
        )

    async def get_market_meta_info(self, symbol: MARKET_SYMBOLS = None):
        """
        Returns a dictionary containing market meta info.
        Inputs:
            symbol(MARKET_SYMBOLS): the market symbol
        Returns:
            dict: meta info
        """
        query = {"symbol": symbol.value} if symbol else {}

        return await self.apis.get(SERVICE_URLS["MARKET"]["META"], query)

    async def get_market_data(self, symbol: MARKET_SYMBOLS = None):
        """
        Returns a dictionary containing market's current data about best ask/bid, 24 hour volume, market price etc..
        Inputs:
            symbol(MARKET_SYMBOLS): the market symbol
        Returns:
            dict: meta info
        """
        query = {"symbol": symbol.value} if symbol else {}

        return await self.apis.get(SERVICE_URLS["MARKET"]["MARKET_DATA"], query)

    async def get_exchange_info(self, symbol: MARKET_SYMBOLS = None):
        """
        Returns a dictionary containing exchange info for market(s). The min/max trade size, max allowed oi open
        min/max trade price, step size, tick size etc...
        Inputs:
            symbol(MARKET_SYMBOLS): the market symbol
        Returns:
            dict: exchange info
        """
        query = {"symbol": symbol.value} if symbol else {}
        return await self.apis.get(SERVICE_URLS["MARKET"]["EXCHANGE_INFO"], query)

    async def get_master_info(self, symbol: MARKET_SYMBOLS = None):
        """
        Returns a dictionary containing master info for market(s).
        It contains all market data, exchange info and meta data of market(s)
        Inputs:
            symbol(MARKET_SYMBOLS): the market symbol
        Returns:
            dict: master info
        """
        query = {"symbol": symbol.value} if symbol else {}
        return await self.apis.get(SERVICE_URLS["MARKET"]["MASTER_INFO"], query)

    async def get_ticker_data(self, symbol: MARKET_SYMBOLS = None):
        """
        Returns a dictionary containing ticker data for market(s).
        Inputs:
            symbol(MARKET_SYMBOLS): the market symbol
        Returns:
            dict: ticker info
        """
        query = {"symbol": symbol.value} if symbol else {}
        return await self.apis.get(SERVICE_URLS["MARKET"]["TICKER"], query)

    async def get_market_candle_stick_data(self, params: GetCandleStickRequest):
        """
        Returns a list containing the candle stick data.
        Inputs:
            params(GetCandleStickRequest): params required to fetch candle stick data
        Returns:
            list: the candle stick data
        """
        params = extract_enums(params, ["symbol", "interval"])

        return await self.apis.get(SERVICE_URLS["MARKET"]["CANDLE_STICK_DATA"], params)

    async def get_market_recent_trades(self, params: GetMarketRecentTradesRequest):
        """
        Returns a list containing the recent trades data.
        Inputs:
            params(GetCandleStickRequest): params required to fetch candle stick data
        Returns:
            ist: the recent trades
        """
        params = extract_enums(params, ["symbol", "traders"])

        return await self.apis.get(SERVICE_URLS["MARKET"]["RECENT_TRADE"], params)

    async def get_contract_addresses(self):
        """
        Returns:
            dict: all contract addresses for the all markets.
        """
        return await self.apis.get(SERVICE_URLS["MARKET"]["CONTRACT_ADDRESSES"])

    ## User endpoints

    def get_account(self):
        """
        Returns the user account object
        """
        return self.account

    def get_public_address(self):
        """
        Returns the user account public address
        """
        return self.account.address

    async def generate_readonly_token(self):
        """
        Returns a read-only token generated for authenticated user.
        """
        return await self.apis.post(
            SERVICE_URLS["USER"]["GENERATE_READONLY_TOKEN"], {}, True
        )

    async def get_orders(self, params: GetOrderRequest):
        """
        Returns a list of orders.
        Inputs:
            params(GetOrderRequest): params required to query orders (e.g. symbol,statuses)
        Returns:
            list: a list of orders
        """
        params = extract_enums(params, ["symbol", "statuses", "orderType"])

        return await self.apis.get(SERVICE_URLS["USER"]["ORDERS"], params, True)

    async def get_transaction_history(self, params: GetTransactionHistoryRequest):
        """
        Returns a list of transaction.
        Inputs:
            params(GetTransactionHistoryRequest): params to query transactions (e.g. symbol)
        Returns:
            list: a list of transactions
        """
        params = extract_enums(params, ["symbol"])
        return await self.apis.get(
            SERVICE_URLS["USER"]["USER_TRANSACTION_HISTORY"], params, True
        )

    async def get_user_position(self, params: GetPositionRequest):
        """
        Returns a list of positions.
        Inputs:
            params(GetPositionRequest): params required to query positions (e.g. symbol)
        Returns:
            list: a list of positions
        """
        params = extract_enums(params, ["symbol"])
        return await self.apis.get(SERVICE_URLS["USER"]["USER_POSITIONS"], params, True)

    async def get_user_trades(self, params: GetUserTradesRequest):
        """
        Returns a list of user trades.
        Inputs:
            params(GetUserTradesRequest): params to query trades (e.g. symbol)
        Returns:
            list: a list of positions
        """
        params = extract_enums(params, ["symbol", "type"])
        return await self.apis.get(SERVICE_URLS["USER"]["USER_TRADES"], params, True)

    async def get_user_account_data(self, parentAddress: str = ""):
        """
        Returns user account data.
        Inputs:
            parentAddress: an optional field, used by sub accounts to fetch parent account state
        """
        return await self.apis.get(
            service_url=SERVICE_URLS["USER"]["ACCOUNT"],
            query={"parentAddress": parentAddress},
            auth_required=True,
        )

    async def get_user_leverage(self, symbol: MARKET_SYMBOLS, parentAddress: str = ""):
        """
        Returns user market default leverage.
        Inputs:
            symbol(MARKET_SYMBOLS): market symbol to get user market default leverage for.
            parentAddress(str): an optional field, used by sub accounts to fetch parent account state
        Returns:
            str: user default leverage
        """
        account_data_by_market = (await self.get_user_account_data(parentAddress))[
            "accountDataByMarket"
        ]

        for i in account_data_by_market:
            if symbol.value == i["symbol"]:
                return from1e18(int(i["selectedLeverage"]))
        # todo fetch from exchange info route
        return DEAULT_EXCHANGE_LEVERAGE

    async def get_cancel_on_disconnect_timer(
        self, params: GetCancelOnDisconnectTimerRequest = None
    ):
        """
        Returns a list of the user's countDowns for provided market symbol,
        Inputs:
            - symbol(MARKET_SYMBOLS): (Optional) market symbol to get user market cancel_on_disconnect timer for, not providing it would return all the active countDown timers for each market.
            - parentAddress (str):(Optional) Only provided by a sub account
        Returns:
            - GetCountDownsResponse:
                - countDowns: object with provided market symbol and respective countDown timer
                - timestamp
        """

        params = extract_enums(params, ["symbol"])
        response = await self.dms_api.get(
            SERVICE_URLS["USER"]["CANCEL_ON_DISCONNECT"], params, auth_required=True
        )
        # check for service unavailibility
        if hasattr(response, "status") and response.status == 503:
            raise Exception(
                "Cancel on Disconnect (dead-mans-switch) feature is currently unavailable"
            )

        return response

    async def reset_cancel_on_disconnect_timer(self, params: PostTimerAttributes):
        """
        Returns PostTimerResponse containing accepted and failed countdowns, and the next page number
        Inputs:
            - params(PostTimerAttributes): params required to fetch funding history
        Returns:
            - PostTimerResponse:
                - acceptedToReset: array with symbols for which timer was reset successfully
                - failedReset: aray with symbols for whcih timer failed to reset
        """
        response = await self.dms_api.post(
            SERVICE_URLS["USER"]["CANCEL_ON_DISCONNECT"],
            json.dumps(params),
            auth_required=True,
            contentType="application/json",
        )
        # check for service unavailibility
        if hasattr(response, "status") and response.status == 503:
            raise Exception(
                "Cancel on Disconnect (dead-mans-switch) feature is currently unavailable"
            )
        return response

    async def _get_coin_having_balance(self, balance: int) -> str:
        usdc_coins_resp = await self.get_usdc_coins()
        usdc_coins = usdc_coins_resp["data"]
        balance = toSuiBase(balance)
        for coin in usdc_coins:
            if int(coin["balance"]) <= balance:
                return coin["coinObjectId"]
        raise Exception(
            "Insufficient balance, please add more SUI tokens or merge your existing tokens"
        )

    async def close_connections(self):
        # close aio http connection
        await self.apis.close_session()
        await self.dms_api.close_session()
