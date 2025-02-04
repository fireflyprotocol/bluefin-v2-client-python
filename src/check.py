from bluefin_rfq_client import *
from pprint import pprint
import asyncio

TEST_ACCT_PHRASE = "strategy glory twin crucial mercy bargain rain list stuff famous moral ketchup"
TEST_NETWORK = "http://127.0.0.1:9000"


async def main():
    wallet = SuiWallet(seed=TEST_ACCT_PHRASE)
    contracts_config = read_json()
    rfq_contracts = RFQContracts(contracts_config)
    rfq_client = RFQClient(wallet=wallet,url=TEST_NETWORK,rfq_contracts=rfq_contracts)
    print(f"Address: {wallet.address}")
    # quote , signature= rfq_client.create_and_sign_quote(
    #     vault="0x67399451f127894ee0f9ff7182cbe914008a0197a97b54e86226d1c33635c368",
    #     quote_id="quote-123",
    #     taker="0x67399451f127894ee0f9ff7182cbe914008a0197a97b54e86226d1c33635c368",
    #     token_in_amount=1,
    #     token_out_amount=1,
    #     token_in_type="0x2::sui::SUI",
    #     token_out_type="0x2::example::TOKEN",
    #     expires_at_utc_sec=1699765400,
    #     created_at_utc_sec=1698765400,
    # )
    # print(f"Signature: {signature}")
    # rfq_client.deposit_in_vault(
    #     vault="0x40923d059eae6ccbbb91ac9442b80b9bec8262122a5756d96021e34cf33f0b1d",
    #     amount="200000000000",
    #     token_type="0x0000000000000000000000000000000000000000000000000000000000000002::sui::SUI"
    # )

    # rfq_client.withdraw_from_vault(
    #     vault="0x40923d059eae6ccbbb91ac9442b80b9bec8262122a5756d96021e34cf33f0b1d",
    #     amount="200000000000",
    #     token_type="0x0000000000000000000000000000000000000000000000000000000000000002::sui::SUI"
    # )

    rfq_client.create_vault(
        manager="0x6f3a49a0003b02be20db759e537e579b57440355cdfa0ae8f5c33e003802a26c"
    )




if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    loop.close()


