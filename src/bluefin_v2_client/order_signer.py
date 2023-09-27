from .utilities import numberToHex, hexToByteArray
from .signer import Signer
from .interfaces import Order
import hashlib


class OrderSigner(Signer):
    def __init__(self, version="1.0"):
        super().__init__()
        self.version = version

    def get_order_flags(self, order):
        """0th bit = ioc
        1st bit = postOnly
        2nd bit = reduceOnly
        3rd bit  = isBuy
        4th bit = orderbookOnly
        e.g. 00000000 // all flags false
        e.g. 00000001 // ioc order, sell side, can be executed by taker
        e.e. 00010001 // same as above but can only be executed by settlement operator
        """
        flag = 0
        if order["ioc"]:
            flag += 1
        if order["postOnly"]:
            flag += 2
        if order["reduceOnly"]:
            flag += 4
        if order["isBuy"]:
            flag += 8
        if order["orderbookOnly"]:
            flag += 16
        return flag

    def get_serialized_order(self, order: Order):
        """
        Returns order hash.
        Inputs:
            - order: the order to be signed
        Returns:
            - str: order hash
        """
        flags = self.get_order_flags(order)
        flags = hexToByteArray(numberToHex(flags, 2))

        buffer = bytearray()
        orderPriceHex = hexToByteArray(numberToHex(int(order["price"])))
        orderQuantityHex = hexToByteArray(numberToHex(int(order["quantity"])))
        orderLeverageHex = hexToByteArray(numberToHex(int(order["leverage"])))
        orderSalt = hexToByteArray(numberToHex(int(order["salt"])))
        orderExpiration = hexToByteArray(numberToHex(int(order["expiration"]), 16))
        orderMaker = hexToByteArray(numberToHex(int(order["maker"], 16), 64))
        orderMarket = hexToByteArray(numberToHex(int(order["market"], 16), 64))
        bluefin = bytearray("Bluefin", encoding="utf-8")

        buffer = (
            orderPriceHex
            + orderQuantityHex
            + orderLeverageHex
            + orderSalt
            + orderExpiration
            + orderMaker
            + orderMarket
            + flags
            + bluefin
        )
        return buffer

    def get_order_hash(self, order: Order):
        buffer = self.get_serialized_order(order)
        return hashlib.sha256(buffer).digest()

    def sign_order(self, order: Order, private_key):
        """
        Used to create an order signature. The method will use the provided key
        in params to sign the order.

        Args:
            order (Order): an order containing order fields (look at Order interface)
            private_key (str): private key of the account to be used for signing

        Returns:
            str: generated signature
        """
        msg_hash = hashlib.sha256(
            self.get_serialized_order(order).hex().encode("utf-8")
        ).digest()
        return self.sign_hash(msg_hash, private_key, "")
