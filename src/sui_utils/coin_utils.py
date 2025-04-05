from .rpc import *
from .signer import Signer
from .account import SuiWallet
from .utilities import *
from .sui_interfaces import Coin
from typing import Tuple, List, Union
from decimal import Decimal

class CoinUtils:
    """
    A Class to handle coin creation, merging, and finding on the SUI chain.
    """
    @staticmethod
    def create_coin_with_balance(coin_type: str, balance: int, wallet: SuiWallet, url: str) -> str:
        """
        Creates a new coin with the specified balance by splitting/merging coins if required.
        Can take long time if the coin is not found and has to merge large number of coins.

        Input:
            coin_type (str): The type of the coin.
            balance (int): The balance for the new coin scaled to coin decimals supported by the coin. Eg: 1000000000 for 1 SUI.
            wallet (SuiWallet): The wallet to sign the transaction.

        Output:
            str: The ID of the new coin.
        """
        try:
            if balance == 0:
                raise ValueError("Currently sdk does not support creating zero coin")

            available_coins = CoinUtils.sort_ascending(get_coins_with_type(wallet.getUserAddress(), coin_type, url))
            available_coins_balance = CoinUtils.sum_coins(available_coins)

            if balance > available_coins_balance:
                raise Exception(f"User: {wallet.getUserAddress()} does not have enough coins of type: {coin_type}")

            coin, has_exact_balance = CoinUtils.find_coin_with_balance(available_coins, balance)

            # if no coin is found, merge all available coins and create a new coin
            if coin is None:
                coin = available_coins[0]
                coin_id = coin.coin_object_id
                # merge all available coins into the first coin
                CoinUtils.merge_coins(available_coins[1:], wallet, url, coin_id)
                # if all coins had exact balance as required, then return the first coin id after merging
                if available_coins_balance == balance:
                    return coin_id
            else:
                coin_id = coin.coin_object_id

            # if the coin is found and has exact balance, return the coin id
            if has_exact_balance:
                return coin_id

            # if the coin has more balance, split the coin and create a new coin
            split_amount = [str(balance)]
            tx_result = CoinUtils.split_coin(coin_id, split_amount, wallet, url)
            if tx_result.effects.status == "success":
                return tx_result.effects.created[0].reference.object_id
            raise Exception("Failed to create coin with balance")
        except Exception as e:
            raise Exception(f"Failed to create coin with balance, Exception: {e}")

    @staticmethod
    def merge_coins(coins: List[Coin], wallet: SuiWallet, url: str, primary_coin_id: str|None = None) -> str:
        """
        Merges provided coins into a primary coin.
        Can take long time to merge large number of coins.
        Recommended to combine with get_all_coins to provide a list of coins to merge.

        Input:
            coins (List[Coin]): List of Coin objects to merge.
            wallet (SuiWallet): The wallet to sign the transaction.
            url (str): The URL of the SUI node.
            primary_coin_id (str): optional ID of the primary coin to merge into. If not provided, the first coin in the list will be used as the primary coin.

        Output:
            str: The ID of the primary coin.
        """
        if primary_coin_id is None:
            primary_coin_id = coins[0].coin_object_id
        
        signer = Signer()
        for coin in coins:
            tx_bytes = rpc_sui_createMergeCoinsTransaction(url, primary_coin_id, coin.coin_object_id, wallet.getUserAddress())
            signer.sign_and_execute_tx(tx_bytes, wallet, url)
        return primary_coin_id
        
    @staticmethod
    def split_coin(coin_id: str, amounts: List[int], wallet: SuiWallet, url: str) -> TransactionResult:
        """
        splits a coin into multiple coins of the specified amounts.

        Input:
            coin_id (str): The ID of the coin to split.
            amounts (List[int]): The amounts of balance required for the new coins [combined must be equal or less than the balance of the provided coin and scaled to supported decimals of the coin. Eg: 1000000000 for 1 SUI]
            wallet (SuiWallet): The wallet to sign the transaction.
            url (str): The URL of the SUI node.
        """
        signer = Signer()
        tx_bytes = rpc_sui_createSplitCoinsTransaction(wallet.getUserAddress(), coin_id, [str(amount) for amount in amounts], url)
        return signer.sign_and_execute_tx(tx_bytes, wallet, url)
        

    @staticmethod
    def find_coin_with_balance(coins: List[Coin], amount: int) -> Tuple[Coin | None, bool]:
        """
        Finds the coin having the provided balance or more.
        Recommended to combine with get_all_coins to provide a list of coins to find the coin with the balance.

        Input:
            coins (List[Coin]): List of Coin objects.
            amount (int): The amount of balance the coin must have scaled to supported decimals of the coin. Eg: 1000000000 for 1 SUI.

        Output:
            Tuple[Coin | None, bool]: The Coin object and a boolean indicating if the coin has exact balance or more.
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
        Recommended to combine with get_all_coins to provide a list of coins to sort.
        Input:
            coins (List[Coin]): List of Coin objects.

        Returns:
            List[Coin]: Sorted list of Coin objects.
        """
        return sorted(coins, key=lambda coin: int(coin.balance))

    @staticmethod
    def sum_coins(coins: List[Coin]) -> int:
        """
        Sums up the balance of all coins.
        Recommended to combine with get_all_coins to provide a list of coins to sum.

        Input:
            coins (List[Coin]): List of Coin objects.

        Returns:
            int: The total balance of all coins.
        """
        return sum(int(coin.balance) for coin in coins)

    @staticmethod
    def get_all_coins(address: str, coin_type: str, url: str) -> List[Coin]:
        """
        Gets all coin objects for an address.
        Input:
            address (str): The address of the user.
            coin_type (str): The type of the coin.
            url (str): The URL of the SUI node.
        Output:
            List[Coin]: A list of Coin objects.
        """
        return get_coins_with_type(address, coin_type, url)


