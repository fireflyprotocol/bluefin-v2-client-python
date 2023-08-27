import socketio
import time
from .enumerations import MARKET_SYMBOLS, SOCKET_EVENTS
import asyncio

sio = socketio.Client()


class Sockets:
    callbacks = {}

    def __init__(self, url, timeout=10, token=None) -> None:
        self.url = url
        self.timeout = timeout
        self.token = token
        self.api_token = ""
        return

    def _establish_connection(self):
        """
        Connects to the desired url
        """
        try:
            sio.connect(self.url, wait_timeout=self.timeout, transports=["websocket"])
            return True
        except:
            return False

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

    async def open(self):
        """
        opens socket instance connection
        """
        self.connection_established = self._establish_connection()
        if not self.connection_established:
            await self.close()
            raise (Exception("Failed to connect to Host: {}".format(self.url)))
        return

    async def close(self):
        """
        closes the socket instance connection
        """
        sio.disconnect()
        return

    @sio.on("*")
    def listener(event, data):
        """
        Listens to all events emitted by the server
        """
        try:
            if event in Sockets.callbacks.keys():
                Sockets.callbacks[event](data)
            elif "default" in Sockets.callbacks.keys():
                Sockets.callbacks["default"]({"event": event, "data": data})
            else:
                pass
        except:
            pass
        return

    @sio.event
    def connect():
        print("Connected To Socket Server")
        # add 10 seconds sleep to allow connection to be established before callbacks for connections are executed
        if "connect" in Sockets.callbacks:
            # Execute the callback using asyncio.run() if available
            time.sleep(10)
            asyncio.run(Sockets.callbacks["connect"]())

    @sio.event
    def disconnect():
        print("Disconnected From Socket Server")
        if "disconnect" in Sockets.callbacks:
            # Execute the callback using asyncio.run() if available
            asyncio.run(Sockets.callbacks["disconnect"]())

    async def listen(self, event, callback):
        """
        Assigns callbacks to desired events
        """
        Sockets.callbacks[event] = callback
        return

    async def subscribe_global_updates_by_symbol(self, symbol: MARKET_SYMBOLS):
        """
        Allows user to subscribe to global updates for the desired symbol.
        Inputs:
            - symbol: market symbol of market user wants global updates for. (e.g. DOT-PERP)
        """
        try:
            if not self.connection_established:
                raise Exception(
                    "Socket connection is established, invoke socket.open()"
                )

            resp = sio.call(
                "SUBSCRIBE",
                [
                    {
                        "e": SOCKET_EVENTS.GLOBAL_UPDATES_ROOM.value,
                        "p": symbol.value,
                    },
                ],
            )
            return resp["success"]
        except Exception as e:
            print("Error: ", e)
            return False

    async def unsubscribe_global_updates_by_symbol(self, symbol: MARKET_SYMBOLS):
        """
        Allows user to unsubscribe to global updates for the desired symbol.
            Inputs:
                - symbol: market symbol of market user wants to remove global updates for. (e.g. DOT-PERP)
        """
        try:
            if not self.connection_established:
                return False

            resp = sio.call(
                "UNSUBSCRIBE",
                [
                    {
                        "e": SOCKET_EVENTS.GLOBAL_UPDATES_ROOM.value,
                        "p": symbol.value,
                    },
                ],
            )

            return resp["success"]
        except Exception as e:
            print(e)
            return False

    async def subscribe_user_update_by_token(
        self, parent_account: str = None, user_token: str = None
    ) -> bool:
        """
        Allows user to subscribe to their account updates.
        Inputs:
            - parent_account(str): address of parent account. Only whitelisted
            sub-account can listen to its parent account position updates
            - token(str): auth token generated when onboarding on Bluefin
        """
        try:
            if not self.connection_established:
                return False

            resp = sio.call(
                "SUBSCRIBE",
                [
                    {
                        "e": SOCKET_EVENTS.USER_UPDATES_ROOM.value,
                        "pa": parent_account,
                        "t": self.token if user_token == None else user_token,
                        "rt": self.api_token,
                    },
                ],
            )

            return resp["success"]
        except Exception as e:
            print(e)
            return False

    async def unsubscribe_user_update_by_token(
        self, parent_account: str = None, user_token: str = None
    ):
        """
        Allows user to unsubscribe to their account updates.
        Inputs:
            - parent_account(str): address of parent account. Only for sub-accounts
            - token: auth token generated when onboarding on Bluefin
        """
        try:
            if not self.connection_established:
                return False

            resp = sio.call(
                "UNSUBSCRIBE",
                [
                    {
                        "e": SOCKET_EVENTS.USER_UPDATES_ROOM.value,
                        "pa": parent_account,
                        "t": self.token if user_token == None else user_token,
                        "rt": self.api_token,
                    },
                ],
            )
            return resp["success"]
        except:
            return False
