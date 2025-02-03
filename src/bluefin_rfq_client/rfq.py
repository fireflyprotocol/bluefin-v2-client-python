from datetime import timezone
from typing import Tuple
from .quote import Quote
from sui_utils import *
from .contracts import RFQContracts

class RFQClient:
    def __init__(self, wallet: SuiWallet = None , url: str = None, rfq_contracts : RFQContracts = None):
        """
        Initializes the RFQClient instance with provided input fields.

        Parameters:
        wallet (SuiWallet): instance of SuiWallet class.
        url (str): RPC url of chain node (e.g https://fullnode.<SUI-NETWORK-VERSION>.sui.io:443)
        rfq_contracts (RFQContracts): instance of RFQContracts class.

        Returns:
        instance of RFQClient.
        """
        if wallet is None:
            raise ValueError(
                "Initialize SuiWallet to use RFQClient")
        if url is None:
            raise ValueError(
                "Please provide rpc url of chain")
        if rfq_contracts is None:
            raise ValueError(
                "Please provide url of chain")
        self.wallet = wallet
        self.url = url
        self.rfq_contracts = rfq_contracts
        self.signer = Signer()

    @staticmethod
    
    def create_quote(
        vault: str,
        quote_id: str,
        taker: str,
        token_in_amount: int,
        token_out_amount: int,
        token_in_type: str,
        token_out_type: str,
        created_at_utc_ms: int = None,
        expires_at_utc_ms: int = None ) -> Quote:
        """
        Creates an instance of Quote with provided params.

        Parameters:
        vault (str): on chain vault object ID.
        quote_id (int): unique quote ID assigned for on chain verification and security.
        taker (str): address of the reciever account.
        token_in_amount (int): amount of the input token reciever is willing to swap [scaled to default base of the coin (i.e for 1 USDC(1e6) , provide input as 1000000 )]
        token_out_amount (int): amount of the output token to be paid by quote initiator [scaled to default base of the coin (i.e for 1 SUI(1e9) , provide input as 1000000000 )]
        token_in_type (str): on chain token type of input coin (i.e for SUI , 0x2::sui::SUI)
        token_out_type (str): on chain token type of output coin (i.e for USDC , usdc_Address::usdc::USDC)
        created_at_utc_ms (int): the unix timestamp at which the quote was created in milliseconds (Defaults to current timestamp)
        expires_at_utc_ms (int): the unix timestamp at which the quote is to be expired in milliseconds ( Defaults to 10 seconds of creation timestamp )

        Returns:
        instance of Quote Class and signature in hex format.
        """

        if created_at_utc_ms is None:
            created_at_utc_ms = int(datetime.now(timezone.utc).timestamp()) * 1000
        if expires_at_utc_ms is None:
            expires_at_utc_ms = created_at_utc_ms + 10000 # 10 seconds expiration

        return Quote(
            vault=vault,
            quote_id=quote_id,
            taker=taker,
            token_in_amount=token_in_amount,
            token_out_amount=token_out_amount,
            token_in_type=token_in_type,
            token_out_type=token_out_type,
            expires_at=expires_at_utc_ms,
            created_at=created_at_utc_ms,
        )

    def sign_quote(self, quote: Quote) -> str:
        """
        Signs the input Quote instance.

        :param quote (Quote): instance of Quote class.

        Returns:
        Signature in hex format.
        """
        bcs_serialized_bytes = Quote.get_bcs_serialized_quote(quote)

        # Sign bcs serialized quote bytes
        signature = self.wallet.sign_personal_msg(bcs_serialized_bytes)
    
        return signature.hex()
    
    def create_and_sign_quote(
        self, 
        vault: str,
        quote_id: str,
        taker: str,
        token_in_amount: int,
        token_out_amount: int,
        token_in_type: str,
        token_out_type: str,
        created_at_utc_ms: int = None,
        expires_at_utc_ms: int = None ) -> Tuple[Quote,str]:

        """
        Creates an instance of Quote with provided params and signs it.

        Parameters:
        vault (str): on chain vault object ID.
        quote_id (int): unique quote ID assigned for on chain verification and security.
        taker (str): address of the reciever account.
        token_in_amount (int): amount of the input token reciever is willing to swap [scaled to default base of the coin (i.e for 1 USDC(1e6) , provide input as 1000000 )]
        token_out_amount (int): amount of the output token to be paid by quote initiator [scaled to default base of the coin (i.e for 1 SUI(1e9) , provide input as 1000000000 )]
        token_in_type (str): on chain token type of input coin (i.e for SUI , 0x2::sui::SUI)
        token_out_type (str): on chain token type of output coin (i.e for USDC , usdc_Address::usdc::USDC)
        created_at_utc_ms (int): the unix timestamp at which the quote was created in milliseconds (Defaults to current timestamp)
        expires_at_utc_ms (int): the unix timestamp at which the quote is to be expired in milliseconds ( Defaults to 10 seconds of creation timestamp )

        Returns:
        Tuple of Quote instance and signature.
        """

        if created_at_utc_ms is None:
            created_at_utc_ms = int(datetime.now(timezone.utc).timestamp())
        if expires_at_utc_ms is None:
            expires_at_utc_ms = created_at_utc_ms + 10000 # 10 seconds expiration

        quote = Quote(
            vault=vault,
            id=quote_id,
            taker=taker,
            token_in_amount=token_in_amount,
            token_out_amount=token_out_amount,
            token_in_type=token_in_type,
            token_out_type=token_out_type,
            expires_at=created_at_utc_ms,
            created_at=created_at_utc_ms,
        )

        bcs_serialized_bytes = Quote.get_bcs_serialized_quote(quote)

        # Sign bcs serialized quote bytes
        signature = self.wallet.sign_personal_msg(bcs_serialized_bytes)
    
        return (quote, signature.hex())
    
    def deposit_in_vault(self, 
        vault: str,
        amount: str,
        token_type: str
        ) -> tuple[bool, dict] :
        """
        Deposits coin amount in the vault.

        Parameters:
        vault (str): on chain vault object ID.
        amount (str): amount of the coin that is to be deposited [scaled to default base of the coin (i.e for 1 USDC(1e6) , provide input as 1000000 )]
        token_type (str): on chain token type of input coin (i.e for USDC , usdc_Address::usdc::USDC)

        Returns:
        Tuple of bool (indicating status of execution) and sui chain response (dict).
        """

        coin_id = get_coin_having_balance(
            user_address=self.wallet.getUserAddress(),
            coin_type=token_type,
            balance=amount,
            url=self.url,
            exact_match=True)
    
        move_function_params = [
                    vault,
                    self.rfq_contracts.get_protocol_config(),
                    coin_id
                ]
        move_function_type_arguments = [
                    token_type
                ]
        
        tx_bytes = rpc_unsafe_moveCall(
            url=self.url,
            params=move_function_params,
            function_name='deposit',
            function_library='gateway',
            userAddress=self.wallet.getUserAddress(),
            packageId=self.rfq_contracts.get_package(),
            gasBudget=1000000000,
            typeArguments=move_function_type_arguments
        )

        signature = self.signer.sign_tx(tx_bytes, self.wallet)
        res = rpc_sui_executeTransactionBlock(self.url, tx_bytes, signature)
        try:
            success = res["result"]["effects"]["status"]["status"] == "success"
            return success, res
        except Exception as e:
            return False , res

    def withdraw_from_vault(self, 
        vault: str,
        amount: str,
        token_type: str
        ) -> tuple[bool, dict] :
        """
        Withdraws coin amount from the vault (Note: Only vault manager can withdraw from vault)

        Parameters:
        vault (str): on chain vault object ID.
        amount (str): amount of the coin that is to be withdrawn [scaled to default base of the coin (i.e for 1 USDC(1e6) , provide input as 1000000 )]
        token_type (str): on chain token type of the coin (i.e for USDC , usdc_Address::usdc::USDC)

        Returns:
        Tuple of bool (indicating status of execution) and sui chain response (dict).
        """
        

    
        move_function_params = [
                    vault,
                    self.rfq_contracts.get_protocol_config(),
                    amount
                ]
        move_function_type_arguments = [
                    token_type
                ]
        
        tx_bytes = rpc_unsafe_moveCall(
            url=self.url,
            params=move_function_params,
            function_name='withdraw',
            function_library='gateway',
            userAddress=self.wallet.getUserAddress(),
            packageId=self.rfq_contracts.get_package(),
            gasBudget=1000000000,
            typeArguments=move_function_type_arguments
        )

        signature = self.signer.sign_tx(tx_bytes, self.wallet)
        res = rpc_sui_executeTransactionBlock(self.url, tx_bytes, signature)
        try:
            success = res["result"]["effects"]["status"]["status"] == "success"
            return success, res
        except Exception as e:
            return False , res
        