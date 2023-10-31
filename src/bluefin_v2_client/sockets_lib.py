import socketio
import time
from .enumerations import MARKET_SYMBOLS, SOCKET_EVENTS
import asyncio
sio = socketio.AsyncClient()


class Sockets:
    callbacks = {}

    def __init__(self, url, timeout=10, token=None) -> None:
        self.url = url
        self.timeout = timeout
        self.token = token
        self.api_token = ""
        return

    async def _establish_connection(self):
        """
            Connects to the desired url
        """
        try:
            await sio.connect(self.url, wait_timeout=self.timeout,
                              transports=["websocket"])
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
        self.connection_established = await self._establish_connection()
        if not self.connection_established:
            await self.close()
            raise (Exception("Failed to connect to Host: {}".format(self.url)))
        return

    async def close(self):
        """
            closes the socket instance connection
        """
        await sio.disconnect()
        return

    @sio.on("*")
    async def listener(event, data):
        """
            Listens to all events emitted by the server
        """
        try:
            if event in Sockets.callbacks.keys():
                await Sockets.callbacks[event](data)
            elif "default" in Sockets.callbacks.keys():
                await Sockets.callbacks["default"]({"event": event, "data": data})
            else:
                pass
        except:
            pass
        return

    @sio.event
    async def connect():
        print("Connected To Socket Server")
        if 'connect' in Sockets.callbacks:
            # Execute the callback using asyncio.run() if available
            await Sockets.callbacks['connect']()

    @sio.event
    async def disconnect():
        print('Disconnected From Socket Server')
        if 'disconnect' in Sockets.callbacks:
            # Execute the callback using asyncio.run() if available
            await Sockets.callbacks['disconnect']()

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
                - symbol: market symbol of market user wants global updates for. (e.g. ETH-PERP)
        """
        try:
            resp = await sio.call('SUBSCRIBE', [
                {
                    "e": SOCKET_EVENTS.GLOBAL_UPDATES_ROOM.value,
                    "p": symbol.value,
                },
            ])
            return resp["success"]
        except Exception as e:
            print("Error: ", e)
            return False

    async def subscribe_orderbook_depth_streams_by_symbol(self, symbol: MARKET_SYMBOLS, depth=""):
        """
            Allows user to subscribe to orderbook depth stream for the desired symbol.
            Inputs:
                - symbol: market symbol of market user wants orderbook depth stream for. (e.g. ETH-PERP)
                - depth: depth of orderbook depth stream (optional)
        """
        try:
            resp = await sio.call('SUBSCRIBE', [
                {
                    "e": SOCKET_EVENTS.ORDERBOOK_DEPTH_STREAM_ROOM.value,
                    "p": symbol.value,
                    "d": depth
                    
                },
            ])
            return resp["success"]
        except Exception as e:
            print("Error: ", e)
            return False

    async def unsubscribe_orderbook_depth_streams_by_symbol(self, symbol: MARKET_SYMBOLS, depth=""):
        """
            Allows user to unsubscribe to orderbook depth stream for the desired symbol.
            Inputs:
                - symbol: market symbol of market user wants orderbook depth stream for. (e.g. ETH-PERP)
                - depth: depth of orderbook depth stream (optional)
        """
        try:
            resp = await sio.call('UNSUBSCRIBE', [
                {
                    "e": SOCKET_EVENTS.ORDERBOOK_DEPTH_STREAM_ROOM.value,
                    "p": symbol.value,
                    "d": depth
                    
                },
            ])
            return resp["success"]
        except Exception as e:
            print("Error: ", e)
            return False

    async def unsubscribe_global_updates_by_symbol(self, symbol: MARKET_SYMBOLS):
        """
            Allows user to unsubscribe to global updates for the desired symbol.
                Inputs:
                    - symbol: market symbol of market user wants to remove global updates for. (e.g. ETH-PERP)
        """
        try:
            resp = await sio.call('UNSUBSCRIBE', [
                {
                    "e": SOCKET_EVENTS.GLOBAL_UPDATES_ROOM.value,
                    "p": symbol.value,
                },
            ])

            return resp["success"]
        except Exception as e:
            print(e)
            return False

    async def subscribe_user_update_by_token(self, parent_account: str = None, user_token: str = None) -> bool:
        """
            Allows user to subscribe to their account updates.
            Inputs:
                - parent_account(str): address of parent account. Only whitelisted 
                  sub-account can listen to its parent account position updates
                - token(str): auth token generated when onboarding on Bluefin
        """
        try:
            resp = await sio.call("SUBSCRIBE", [
                {
                    "e": SOCKET_EVENTS.USER_UPDATES_ROOM.value,
                    'pa': parent_account,
                    "t": self.token if user_token == None else user_token,
                    "rt": self.api_token
                },
            ])

            return resp["success"]
        except Exception as e:
            print(e)
            return False

    async def unsubscribe_user_update_by_token(self, parent_account: str = None, user_token: str = None):
        """
            Allows user to unsubscribe to their account updates.
            Inputs:
                - parent_account(str): address of parent account. Only for sub-accounts
                - token: auth token generated when onboarding on Bluefin
        """
        try:
            resp = await sio.call("UNSUBSCRIBE", [
                {
                    "e": SOCKET_EVENTS.USER_UPDATES_ROOM.value,
                    'pa': parent_account,
                    "t": self.token if user_token == None else user_token,
                    "rt": self.api_token
                },
            ])
            return resp["success"]
        except:
            return False
