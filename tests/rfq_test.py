import unittest
import base64

from sui_utils.enumerations import WALLET_SCHEME
from bluefin_rfq_client.rfq import RFQClient
from bluefin_rfq_client.quote import Quote
from bluefin_rfq_client.contracts import RFQContracts
from sui_utils import SuiWallet

TEST_ACCT_SEED = "lawsuit pony abuse faint call ship attract slender arrange expire despair orbit"
TEST_RFQ_CONTRACTS = {
        "ProtocolConfig": "0x27cbb31ab9f1ab48331021e054918fbb5f10b2a708feb9c983665ffb56cd8a98",
        "AdminCap": "0x2e5ac6dd340b6475c629fb7c7c425fe571ae0c763e64601307d2690230cd00bd",
        "Package": "0x3cf09d732b53b4270cab290e1c2a6fbd2f7ac8c1f205be90a302d7da23646801",
        "UpgradeCap": "0xae729f710b6017251f846e8ba01ba3cdf28949bbb3615f6274f72fc2c07b5838",
        "BasePackage": "0x3cf09d732b53b4270cab290e1c2a6fbd2f7ac8c1f205be90a302d7da23646801",
        "vaults": ["0x4f452732b2f1be3fda125eaba2d7fc82e7ed1c6deabefe728386c51e9c5c8469"]
    }

class TestRFQ(unittest.TestCase):

    def setUp(self):
        self.wallet = SuiWallet(seed=TEST_ACCT_SEED,scheme=WALLET_SCHEME.ED25519)
        self.url = "https://fullnode.testnet.sui.io:443"
        self.rfq_contracts = RFQContracts(TEST_RFQ_CONTRACTS)
        self.client = RFQClient(wallet=self.wallet, url=self.url, rfq_contracts=self.rfq_contracts)

    def test_get_bcs_serialized_quote(self):
        vault = "0x4f452732b2f1be3fda125eaba2d7fc82e7ed1c6deabefe728386c51e9c5c8469"
        quote_id = "quote_id"
        taker = "0x3cf09d732b53b4270cab290e1c2a6fbd2f7ac8c1f205be90a302d7da23646801"
        token_in_amount = 1000000
        token_out_amount = 1000000000
        token_in_type = "0x2::sui::SUI"
        token_out_type = "usdc_Address::usdc::USDC"
        created_at_utc_ms = 1739649099673
        expires_at_utc_ms = 1739649099673 + 10000

        quote = Quote(
            vault=vault,
            id=quote_id,
            taker=taker,
            token_in_amount=token_in_amount,
            token_out_amount=token_out_amount,
            token_in_type=token_in_type,
            token_out_type=token_out_type,
            created_at=created_at_utc_ms,
            expires_at=expires_at_utc_ms
        )

        serialized_quote = quote.get_bcs_serialized_quote()
        self.assertIsInstance(serialized_quote, bytes)
        self.assertEqual(len(serialized_quote), 144) 
        self.assertEqual(serialized_quote.hex(),"4f452732b2f1be3fda125eaba2d7fc82e7ed1c6deabefe728386c51e9c5c84690871756f74655f69643cf09d732b53b4270cab290e1c2a6fbd2f7ac8c1f205be90a302d7da2364680140420f000000000000ca9a3b000000000d3078323a3a7375693a3a53554918757364635f416464726573733a3a757364633a3a55534443a9ce2a0b9501000099a72a0b95010000")


    def test_create_and_sign_quote(self):
        vault = "0x4f452732b2f1be3fda125eaba2d7fc82e7ed1c6deabefe728386c51e9c5c8469"
        quote_id = "quote_id"
        taker = "0x3cf09d732b53b4270cab290e1c2a6fbd2f7ac8c1f205be90a302d7da23646801"
        token_in_amount = 1000000
        token_out_amount = 1000000000
        token_in_type = "0x2::sui::SUI"
        token_out_type = "usdc_Address::usdc::USDC"
        created_at_utc_ms = 1739649099673
        expires_at_utc_ms = 1739649099673 + 10000

        quote, signature = self.client.create_and_sign_quote(
            vault=vault,
            quote_id=quote_id,
            taker=taker,
            token_in_amount=token_in_amount,
            token_out_amount=token_out_amount,
            token_in_type=token_in_type,
            token_out_type=token_out_type,
            created_at_utc_ms=created_at_utc_ms,
            expires_at_utc_ms=expires_at_utc_ms
        )

        self.assertIsInstance(quote, Quote)
        self.assertIsInstance(signature, str)
        self.assertEqual(quote.vault, vault)
        self.assertEqual(quote.id, quote_id)
        self.assertEqual(quote.taker, taker)
        self.assertEqual(quote.token_in_amount, token_in_amount)
        self.assertEqual(quote.token_out_amount, token_out_amount)
        self.assertEqual(quote.token_in_type, token_in_type)
        self.assertEqual(quote.token_out_type, token_out_type)
        self.assertEqual(quote.created_at, created_at_utc_ms)
        self.assertEqual(quote.expires_at, expires_at_utc_ms)
        
        signature_bytes = base64.b64decode(signature)
        self.assertEqual(len(signature_bytes), 97) # 1 byte for scheme + 64 bytes for signature + 32 bytes for public key
        self.assertEqual(signature, 'AI2hMIwpMejH79EWlsVvxBS3xR4AUvLu6Sn/VkjWdg1GXTPcKCe2qnuwqiJ9NRBfeh0OJN0WOr3jQ3rUbwZEBgYyv4X57To4RF3VKtJcBX/4mzphZ2lN9+6UdZZK8/UEtw==')

    def test_quote_signature(self):

        quote = Quote(
            vault="0x4f452732b2f1be3fda125eaba2d7fc82e7ed1c6deabefe728386c51e9c5c8469",
            id="quote_id",
            taker="0x3cf09d732b53b4270cab290e1c2a6fbd2f7ac8c1f205be90a302d7da23646801",
            token_in_amount=1000000,
            token_out_amount=1000000000,
            token_in_type="0x2::sui::SUI",
            token_out_type="address::blue::BLUE",
            created_at=1739649099674,
            expires_at=1739649099674 + 10000
        )
        
        signature = quote.sign(self.wallet)
        self.assertEqual(len(signature), 97)
        self.assertEqual(signature.hex(),'00c72ac6755ac69cb47c52a79507da29df222bf30bb4cc336c01026baf69cbff6a18a8be7b01ed6e24b2276104c718dd4d1c4a76ec635fe19dfe5aec09b3174e0f32bf85f9ed3a38445dd52ad25c057ff89b3a6167694df7ee9475964af3f504b7')  # 1 byte for scheme + 64 bytes for signature + 32 bytes for public key
    
    def test_quote_signature_failure(self):

        quote = Quote(
            vault="0x4f452732b2f1be3fda125eaba2d7fc82e7ed1c6deabefe728386c51e9c5c8469",
            id="quote_id",
            taker="0x3cf09d732b53b4270cab290e1c2a6fbd2f7ac8c1f205be90a302d7da23646801",
            token_in_amount=1000000,
            token_out_amount=1000000000,
            token_in_type="0x2::sui::SUI",
            token_out_type="address::blue::BLUE",
            created_at=1739649099674,
            expires_at=1739649099674 + 10000
        )
        
        signature = quote.sign(self.wallet)
        self.assertEqual(len(signature), 97)
        self.assertEqual(signature.hex(),'00c72ac6755ac69cb47c52a79507da29df222bf30bb4cc336c01026baf69cbff6a18a8be7b01ed6e24b2276104c718dd4d1c4a76ec635fe19dfe5aec09b3174e0f32bf85f9ed3a38445dd52ad25c057ff89b3a6167694df7ee9475964af3f504b7')  # 1 byte for scheme + 64 bytes for signature + 32 bytes for public key

    def test_signature_verification_success(self):
        quote = Quote(
            vault="0x4f452732b2f1be3fda125eaba2d7fc82e7ed1c6deabefe728386c51e9c5c8469",
            id="quote_id",
            taker="0x3cf09d732b53b4270cab290e1c2a6fbd2f7ac8c1f205be90a302d7da23646801",
            token_in_amount=1000000,
            token_out_amount=1000000000,
            token_in_type="0x2::sui::SUI",
            token_out_type="address::blue::BLUE",
            created_at=1739649099674,
            expires_at=1739649099674 + 10000
        )
        
        signature = quote.sign(self.wallet)
        signerAddress = self.wallet.getUserAddress()
        self.assertTrue(quote.verify_signature(signature.hex(), signerAddress))
    
    def test_signature_verification_failure(self):
        quote = Quote(
            vault="0x4f452732b2f1be3fda125eaba2d7fc82e7ed1c6deabefe728386c51e9c5c8469",
            id="quote_id",
            taker="0x3cf09d732b53b4270cab290e1c2a6fbd2f7ac8c1f205be90a302d7da23646801",
            token_in_amount=1000000,
            token_out_amount=1000000000,
            token_in_type="0x2::sui::SUI",
            token_out_type="address::blue::BLUE",
            created_at=1739649099674,
            expires_at=1739649099674 + 10000
        )
        
        signature = quote.sign(self.wallet)
        signerAddress = self.wallet.getUserAddress()
        # modify signature byte
        signature = bytearray(signature)
        signature[10] = 1
        self.assertFalse(quote.verify_signature(signature.hex(), signerAddress))

if __name__ == '__main__':
    unittest.main()
