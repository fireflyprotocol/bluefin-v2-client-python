# RFQClient
A Python-based client for interacting with Bluefin RFQ (Request for Quote) protocol on the Sui blockchain. This library module allows users to create, sign, and manage quotes, as well as deposit and withdraw assets from vaults.

## Features
- Initialize an RFQClient with a `SuiWallet`.
- Create and sign quotes for token swaps.
- Deposit tokens into a vault.
- Withdraw tokens from a vault (vault manager only).

## Installation
To use `RFQClient`, ensure you have Python installed and install the necessary dependencies.


The package can be installed from [PyPi](https://pypi.org/project/bluefin-v2-client-python/) using pip:

```bash
pip install bluefin_v2_client_sui
```

## Usage

### Importing the Library
```python
from bluefin_rfq_client import *
```

### RFQ Contracts config 
At the root of your working directory, create `contacts.json` and add the contract configs, eg.
```json
{
    "UpgradeCap": "0x23cffdc270102d2dbb36546ef202e7be100d1a56cc0e508eef505efd240988e3",
    "ProtocolConfig": "0x7b8a9994e1887c82cfd925bd511abb33f8e2cf045fc6e605c73c2e8d51e89dba",
    "Package": "0x872809300103e7812e6b515d277488ad747aecc6a0f537097a96ea0865c3952a",
    "AdminCap": "0xa04ab81dcd60867f785639500d22dfd3fabdbed3b6daeac7d6bb2cd0745a3c3b",
    "BasePackage": "0x872809300103e7812e6b515d277488ad747aecc6a0f537097a96ea0865c3952a",
    "vaults": ["0x40923d059eae6ccbbb91ac9442b80b9bec8262122a5756d96021e34cf33f0b1d"]
}

```
>Note: These are different for mainnet/testnet

### Initializing the Client
```python
# Seed phrase (mnemonic) of the wallet
TEST_ACCT_PHRASE = "wallet seed phrase" 
# RPC URL of the chain
TEST_NETWORK = "https://fullnode.mainnet.sui.io:443"

# Initialize SuiWallet using seed
wallet = SuiWallet(seed=TEST_ACCT_PHRASE)

# Read the contracts config (you can also specify filepath as an argument to read_json, by default it looks for contracts.json at root of working directory )
contracts_config = read_json()

# Initialize RFQContracts instance using the contract conffigs
rfq_contracts = RFQContracts(contracts_config)

# Initialize RFQClient
rfq_client = RFQClient(wallet=wallet, url=TEST_NETWORK, rfq_contracts=rfq_contracts)

```

### Creating and Signing a Quote

#### Parameters:
- `vault` (str): On-chain vault object ID.
- `quote_id` (str): Unique quote ID.
- `taker` (str): Address of the receiver.
- `token_in_amount` (int): Amount of the input token.
- `token_out_amount` (int): Amount of the output token.
- `token_in_type` (str): On-chain token type of input coin.
- `token_out_type` (str): On-chain token type of output coin.
- `created_at_utc_ms` (int, optional): Creation UTC timestamp (default: current time).
- `expires_at_utc_ms` (int, optional): Expiry UTC timestamp (default: 10 seconds after creation timestamp).

```python

# To only create the quote use
quote = rfq_client.create_quote(
    vault="0x67399451f127894ee0f9ff7182cbe914008a0197a97b54e86226d1c33635c368",
    quote_id="quote-123",
    taker="0x67399451f127894ee0f9ff7182cbe914008a0197a97b54e86226d1c33635c368",
    token_in_amount=1000000000,
    token_out_amount=200000000,
    token_in_type="0x2::sui::SUI",
    token_out_type="0x2::example::TOKEN",
    created_at_utc_ms=1699765400,
    created_at_utc_ms=1698765400,
)

#To create quote and sign it at the same time, use
quote, signature = rfq_client.create_and_sign_quote(
    vault="0x67399451f127894ee0f9ff7182cbe914008a0197a97b54e86226d1c33635c368",
    quote_id="quote-123",
    taker="0x67399451f127894ee0f9ff7182cbe914008a0197a97b54e86226d1c33635c368",
    token_in_amount=1000000000,
    token_out_amount=200000000,
    token_in_type="0x2::sui::SUI",
    token_out_type="0x2::example::TOKEN",
    created_at_utc_ms=1699765400,
    created_at_utc_ms=1698765400,
)
```

### Depositing Tokens into a Vault
```python
rfq_client.deposit_in_vault(
    vault="0x40923d059eae6ccbbb91ac9442b80b9bec8262122a5756d96021e34cf33f0b1d",
    amount="200000000000",
    token_type="0x0000000000000000000000000000000000000000000000000000000000000002::sui::SUI"
)
```

### Withdrawing Tokens from a Vault
```python
rfq_client.withdraw_from_vault(
    vault="0x40923d059eae6ccbbb91ac9442b80b9bec8262122a5756d96021e34cf33f0b1d",
    amount="200000000000"
    token_type="0x0000000000000000000000000000000000000000000000000000000000000002::sui::SUI"
)
```

### Creating a new Vault
```python
rfq_client.create_vault(
    manager="0x40923d059eae6ccbbb91ac9442b80b9bec8262122a5756d96021e34cf33f0b1d",
)
```

## API Reference

#### `RFQClient(wallet: SuiWallet, url: str, rfq_contracts: RFQContracts)`
Initializes the RFQClient.

##### Parameters:
- `wallet` (SuiWallet): Instance of SuiWallet.
- `url` (str): RPC URL of the chain node.
- `rfq_contracts` (RFQContracts): Instance of RFQContracts.

#### `create_quote(...) -> Quote`</br>`sign_quote(quote: Quote) -> str`</br> `create_and_sign_quote(...) -> Tuple[Quote, str]`


Creates or/and signs a quote.

##### Parameters:
- `vault` (str): On-chain vault object ID.
- `quote_id` (str): Unique quote ID.
- `taker` (str): Address of the receiver.
- `token_in_amount` (int): Amount of the input token.
- `token_out_amount` (int): Amount of the output token.
- `token_in_type` (str): On-chain token type of input coin.
- `token_out_type` (str): On-chain token type of output coin.
- `created_at_utc_ms` (int, optional): Creation UTC timestamp in milliseconds (default: current time).
- `expires_at_utc_ms` (int, optional): Expiry UTC timestamp in milliseconds (default: 10 seconds after creation timestamp).

#### `deposit_in_vault(vault: str, amount: str, token_type: str) -> Tuple[bool, dict]`
Deposits a token amount into the vault.

#### `withdraw_from_vault(vault: str, amount: str, token_type: str) -> Tuple[bool, dict]`
Withdraws a token amount from the vault (only vault manager can withdraw).

#### `def create_vault(self, manager: str ) -> tuple[bool, dict]`
Creates a new vault on bluefin rfq protocol with provided vault manager.


## Contact
For issues and inquiries, please open a GitHub issue.

