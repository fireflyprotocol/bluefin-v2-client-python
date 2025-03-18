from .rpc import *
from .signer import Signer
from .account import SuiWallet
from .utilities import *
from .sui_interfaces import Coin
from typing import Tuple, List, Union
from decimal import Decimal

class CoinUtils:
    def __init__(self, url: str, sui_wallet: SuiWallet = None):
        self.sui_wallet = sui_wallet
        self.url = url
        self.signer = Signer()

    def create_coin_with_balance(self, coin_type: str, balance: int, wallet: SuiWallet) -> str:
        """
        Creates a new coin with the specified balance by splitting/merging coins if required.

        Parameters:
        coin_type (str): The type of the coin.
        balance (int): The balance for the new coin scaled to coin decimals.
        wallet (SuiWallet): The wallet to sign the transaction.

        Returns:
        str: The ID of the new coin.
        """
        try:
            if wallet is None:
                wallet = self.sui_wallet
            if wallet is None:
                raise ValueError("SuiWallet is not provided")
            if balance == 0:
                return self.create_zero_coin(coin_type, self.url, wallet)

            available_coins = self.sort_ascending(get_coins_with_type(wallet.getUserAddress(), coin_type, self.url))
            available_coins_balance = self.sum_coins(available_coins)

            if balance > available_coins_balance:
                raise Exception(f"User: {wallet.getUserAddress()} does not have enough coins: {coin_type}")

            coin, has_exact_balance = self.find_coin_with_balance(available_coins, balance)

            if coin is None:
                coin = available_coins[0]
                coin_id = coin.coin_object_id
                self.merge_coins(coin_id, available_coins[1:], wallet)
            else:
                coin_id = coin.coin_object_id

            if has_exact_balance:
                return coin_id

            split_amounts = [str(balance)]
            tx_bytes = rpc_sui_createSplitCoinsTransaction(wallet.getUserAddress(), coin_id, split_amounts, self.url)
            result = self.signer.sign_and_execute_tx(tx_bytes, wallet, self.url)
            if result.effects.status == "success":
                for obj in result.effects.mutated:
                    if obj.reference.object_id != coin_id:
                        return obj.reference.object_id
            raise Exception("Failed to create coin with balance")
        except Exception as e:
            raise Exception(f"Failed to create coin with balance, Exception: {e}")

    def create_zero_coin(self, coin_type: str, url: str, wallet: SuiWallet = None) -> str:
        """
        Creates a new coin with zero balance.

        Parameters:
        coin_type (str): The type of the coin.
        wallet (SuiWallet): The wallet to sign the transaction.

        Returns:
        str: The ID of the new coin.
        """
        try:
            if wallet is None:
                wallet = self.sui_wallet
            if wallet is None:
                raise ValueError("SuiWallet is not provided")
            
            tx_bytes = rpc_unsafe_moveCall(
                    url=url,
                    packageId=SUI_NATIVE_PACKAGE_ID,
                    function_library="coin",
                    function_name="zero",
                    params=[],
                    typeArguments=[coin_type],
                    userAddress=wallet.address,
                    gasBudget="10000"
            )

            result = self.signer.sign_and_execute_tx(tx_bytes=tx_bytes, sui_wallet=wallet,url=url)

            if result.effects.status == "success":
                for obj in result.effects.mutated:
                    return obj.reference.object_id
            raise Exception("Failed to create zero coin")
        except Exception as e:
            raise Exception(f"Failed to create zero coin, Exception: {e}")

    def merge_coins(self, primary_coin_id: str, coins: List[Coin], wallet: SuiWallet):
        """
        Merges multiple coins into a primary coin.

        Parameters:
        primary_coin_id (str): The ID of the primary coin to merge into.
        coins (List[Coin]): List of Coin objects to merge.
        wallet (SuiWallet): The wallet to sign the transaction.
        """
        for coin in coins:
            tx_bytes = rpc_sui_mergeCoins(self.url, primary_coin_id, coin.coin_object_id, wallet.getUserAddress())
            self.signer.sign_and_execute_tx(tx_bytes, wallet, self.url)

    @staticmethod
    def find_coin_with_balance(coins: List[Coin], amount: int) -> Tuple[Union[Coin, None], bool]:
        """
        Finds the coin having the provided balance. If none then returns None.

        Parameters:
        coins (List[Coin]): List of Coin objects.
        amount (int): The amount of balance the coin must have.

        Returns:
        Tuple[Union[Coin, None], bool]: The Coin object and a boolean indicating if the coin has exact balance or more.
        """
        for coin in coins:
            coin_balance = int(coin.balance)
            if coin_balance >= amount:
                return coin, coin_balance == amount
        return None, False

    @staticmethod
    def sort_ascending(coins: List[Coin]) -> List[Coin]:
        """
        Sorts the list of coins in ascending order based on their balance.

        Parameters:
        coins (List[Coin]): List of Coin objects.

        Returns:
        List[Coin]: Sorted list of Coin objects.
        """
        return sorted(coins, key=lambda coin: int(coin.balance))

    @staticmethod
    def sum_coins(coins: List[Coin]) -> int:
        """
        Sums up the balance of all coins.

        Parameters:
        coins (List[Coin]): List of Coin objects.

        Returns:
        int: The total balance of all coins.
        """
        return sum(int(coin.balance) for coin in coins)


