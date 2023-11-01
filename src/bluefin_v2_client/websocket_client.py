import json
import logging
from .socket_manager import SocketManager
from .enumerations import MARKET_SYMBOLS, SOCKET_EVENTS


class WebsocketClient:
    def __init__(
        self,
        stream_url,
        token=None,
        api_token=None,
        logger=None,
    ):
        if not logger:
            logger = logging.getLogger(__name__)
        self.logger = logger
        self.token = token
        self.api_token = api_token
        self.stream_url = stream_url
        self.callbacks = {}

    def initialize_socket(
        self,
        on_open,
        on_close=None,
        on_error=None,
        on_ping=None,
        on_pong=None,
        logger=None,
    ):
        self.socket_manager = SocketManager(
            self.stream_url,
            on_message=self.listener,
            on_open=on_open,
            on_close=on_close,
            on_error=on_error,
            on_ping=on_ping,
            on_pong=on_pong,
            logger=logger,
        )

        # start the thread
        self.socket_manager.create_ws_connection()
        self.logger.debug("WebSocket Client started.")
        self.socket_manager.start()

    def set_token(self, token):
        """
        Sets default user token
        Inputs:
            - token (user auth token): Bluefin onboarding token.
        """
        self.token = token

    def set_api_token(self, token):
        """
        Sets default user token
        Inputs:
            - token (user auth token): Bluefin onboarding token.
        """
        self.api_token = token

    def listen(self, event, callback):
        """
        Assigns callbacks to desired events
        """
        self.callbacks[event] = callback
        return

    def send(self, message: dict):
        self.socket_manager.send_message(json.dumps(message))

    def subscribe_global_updates_by_symbol(self, symbol: MARKET_SYMBOLS):
        """
        Allows user to subscribe to global updates for the desired symbol.
        Inputs:
            - symbol: market symbol of market user wants global updates for. (e.g. ETH-PERP)
        """
        try:
            if not self.socket_manager.ws.connected:
                raise Exception(
                    "Socket connection is established, invoke socket.open()"
                )

            self.socket_manager.send_message(
                json.dumps(
                    [
                        "SUBSCRIBE",
                        [
                            {
                                "e": SOCKET_EVENTS.GLOBAL_UPDATES_ROOM.value,
                                "p": symbol.value,
                            },
                        ],
                    ]
                )
            )
            return True
        except Exception:
            return False

    def unsubscribe_global_updates_by_symbol(self, symbol: MARKET_SYMBOLS):
        """
        Allows user to unsubscribe to global updates for the desired symbol.
            Inputs:
                - symbol: market symbol of market user wants to remove global updates for. (e.g. ETH-PERP)
        """
        try:
            if not self.socket_manager.ws.connected:
                return False

            self.socket_manager.send_message(
                json.dumps(
                    (
                        [
                            "UNSUBSCRIBE",
                            [
                                {
                                    "e": SOCKET_EVENTS.GLOBAL_UPDATES_ROOM.value,
                                    "p": symbol.value,
                                },
                            ],
                        ]
                    )
                )
            )
            return True
        except:
            return False
    
    async def subscribe_orderbook_depth_streams_by_symbol(self, symbol: MARKET_SYMBOLS, depth=""):
        """
            Allows user to subscribe to orderbook depth stream for the desired symbol.
            Inputs:
                - symbol: market symbol of market user wants orderbook depth stream for. (e.g. ETH-PERP)
                - depth: depth of orderbook depth stream (optional)
        """
        try:
            self.socket_manager.send_message(json.dumps((['SUBSCRIBE', [
                {
                    "e": SOCKET_EVENTS.ORDERBOOK_DEPTH_STREAM_ROOM.value,
                    "p": symbol.value,
                    "d": depth
                    
                },
            ]])))
            return True
        except:
            return False

    async def subscribe_orderbook_depth_streams_by_symbol(self, symbol: MARKET_SYMBOLS, depth=""):
        """
            Allows user to subscribe to orderbook depth stream for the desired symbol.
            Inputs:
                - symbol: market symbol of market user wants orderbook depth stream for. (e.g. ETH-PERP)
                - depth: depth of orderbook depth stream (optional)
        """
        try:
            self.socket_manager.send_message(json.dumps((['UNSUBSCRIBE', [
                {
                    "e": SOCKET_EVENTS.ORDERBOOK_DEPTH_STREAM_ROOM.value,
                    "p": symbol.value,
                    "d": depth
                    
                },
            ]])))
            return True
        except:
            return False


    def subscribe_user_update_by_token(self, user_token: str = None):
        """
        Allows user to subscribe to their account updates.
        Inputs:
            - token(str): auth token generated when onboarding on Bluefin
        """
        try:
            if not self.socket_manager.ws.connected:
                return False

            self.socket_manager.send_message(
                json.dumps(
                    (
                        [
                            "SUBSCRIBE",
                            [
                                {
                                    "e": SOCKET_EVENTS.USER_UPDATES_ROOM.value,
                                    "t": self.token
                                    if user_token == None
                                    else user_token,
                                    "rt": self.api_token,
                                },
                            ],
                        ]
                    )
                )
            )
            return True
        except:
            return False

    def unsubscribe_user_update_by_token(self, user_token: str = None):
        """
        Allows user to unsubscribe to their account updates.
        Inputs:
            - token: auth token generated when onboarding on Bluefin
        """
        try:
            if not self.socket_manager.ws.connected:
                return False

            self.socket_manager.send_message(
                json.dumps(
                    (
                        [
                            "UNSUBSCRIBE",
                            [
                                {
                                    "e": SOCKET_EVENTS.USER_UPDATES_ROOM.value,
                                    "t": self.token
                                    if user_token == None
                                    else user_token,
                                    "rt": self.api_token,
                                },
                            ],
                        ]
                    )
                )
            )
            return True
        except:
            return False

    def ping(self):
        self.logger.debug("Sending ping to WebSocket Server")
        self.socket_manager.ping()

    def stop(self, id=None):
        self.socket_manager.close()
        # self.socket_manager.join()

    def listener(self, _, message):
        """
        Listens to all events emitted by the server
        """
        data = json.loads(message)
        event_name = data["eventName"]
        try:
            if event_name in self.callbacks:
                callback = self.callbacks[event_name]
                callback(data["data"])
            elif "default" in self.callbacks.keys():
                self.callbacks["default"]({"event": event_name, "data": data["data"]})
            else:
                pass
        except:
            pass
        return
