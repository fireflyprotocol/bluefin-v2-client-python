# RFQClient

A Python-based client for interacting with Bluefin RFQ (Request for Quote) protocol on the Sui blockchain. This library module allows users to create, sign, and manage quotes, as well as deposit and withdraw assets from vaults.

## Features

- Initialize an RFQClient with a `SuiWallet`.
- Create and sign quotes for token swaps.
- Deposit tokens into a vault.
- Withdraw tokens from a vault (vault manager only).
- Update vault manager and coin configurations.
- Query vault balances.

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

At the root of your working directory, create `rfq-contracts.json` and add the contract configs, eg.

```json
{
  "AdminCap": "0x4e39464652a02bada3332ca5bcd03744fd8d6c1a6aee0e40bc52c1ce10e8ecce",
  "ProtocolConfig": "0xc6b29a60c3924776bedc78df72c127ea52b86aeb655432979a38f13d742dedaa",
  "UpgradeCap": "0xe94ed0534120596d2e44d67aa4502b1c327da0b65c2340444e4baf67558a6911",
  "Package": "0xe1c74115896c6d66e7e9569f767628bf472584eea69cbc7ebe378430866b1c86",
  "BasePackage": "0xf8870f988ab09be7c5820a856bd5e9da84fc7192e095a7a8829919293b00a36c",
  "vaults": [
    "0xd03a88fea3a40facd4218cdb230ea4626e6b946ab814866cdfaf45729579ae4e",
    "0x76441b56cb8e410ffa0fdde6760fca111d0b60ed2d741ee35b944a9bfbcc41d0"
  ]
}
```


### Initializing the Client

```python
# Seed phrase (mnemonic) of the wallet (currently supports only ED25519)
TEST_ACCT_PHRASE = "wallet seed phrase"
# RPC URL of the chain
TEST_NETWORK = "https://fullnode.mainnet.sui.io:443"

# Initialize SuiWallet using seed
wallet = SuiWallet(seed=TEST_ACCT_PHRASE)

# Read the contracts config (you can also specify filepath as an argument to read_json(filepath), by default it looks for rfq-contracts.json at root of working directory )
contracts_config = read_json()

# Initialize RFQContracts instance using the contract conffigs
rfq_contracts = RFQContracts(contracts_config)

# Initialize RFQClient
rfq_client = RFQClient(wallet=wallet, url=TEST_NETWORK, rfq_contracts=rfq_contracts)
```

### Creating and Signing a Quote

#### Supported wallets (No hashing required):

- `ED25519`

#### Parameters:

- `vault` (str): On-chain vault object ID.
- `quote_id` (str): Unique quote ID.
- `taker` (str): Address of the receiver.
- `token_in_amount` (int): Amount of the input token ()
- `token_out_amount` (int): Amount of the output token.
- `token_in_type` (str): On-chain token type of input coin.
- `token_out_type` (str): On-chain token type of output coin.
- `created_at_utc_ms` (int, optional): Creation UTC timestamp (default: current time).
- `expires_at_utc_ms` (int, optional): Expiry UTC timestamp (default: 30 seconds after creation timestamp).

```python
# To only create the quote, use
quote = rfq_client.create_quote(
    vault="0x67399451f127894ee0f9ff7182cbe914008a0197a97b54e86226d1c33635c368",
    quote_id="quote-123",
    taker="0x67399451f127894ee0f9ff7182cbe914008a0197a97b54e86226d1c33635c368",
    token_in_amount=1000000000, # (scaled to supported coin decimals, eg. 1000000000 for 1 Sui)
    token_out_amount=200000000, # (scaled to supported coin decimals, eg. 1000000 for 1 USDC)
    token_in_type="0x2::sui::SUI",
    token_out_type="0x2::example::TOKEN",
    expired_at_utc_ms=1699765400,
    created_at_utc_ms=1698765400,
)

# To sign the created quote, use
quote.sign(rfq_client.wallet)

# To create quote and sign it at the same time, use
quote, signature = rfq_client.create_and_sign_quote(
    vault="0x67399451f127894ee0f9ff7182cbe914008a0197a97b54e86226d1c33635c368",
    quote_id="quote-123",
    taker="0x67399451f127894ee0f9ff7182cbe914008a0197a97b54e86226d1c33635c368",
    token_in_amount=1000000000, # (scaled to supported coin decimals, eg. 1000000000 for 1 Sui)
    token_out_amount=200000000, # (scaled to supported coin decimals, eg. 1000000 for 1 USDC)
    token_in_type="0x2::sui::SUI",
    token_out_type="0x2::example::TOKEN",
    expired_at_utc_ms=1699765400,
    created_at_utc_ms=1698765400,
)
```

### Creating a new Vault

#### Supported wallets (blake2b hashing required, since its a sui transaction):

- `ED25519`

```python
rfq_client.create_vault(
    manager="0x40923d059eae6ccbbb91ac9442b80b9bec8262122a5756d96021e34cf33f0b1d",
    gasbudget="100000000"  # Optional, defaults to 0.1 Sui
)
```

### Adding support for a coin in the vault (Only vault manager)

#### Supported wallets (blake2b hashing required, since its a sui transaction):

- `ED25519`

```python
rfq_client.add_coin_support(
    vault="0x84511b56cb8e410ffa0fdde6760fca111d0b60ed2d741ee35b944a9bfbcc3456",
    coin_type="0xdba34672e30cb065b1f93e3ab55318768fd6fef66c15942c9f7cb846e2f900e7::usdc::USDC", 
    min_amount="1000000",  # (scaled to supported coin decimals, eg. 1000000000 for 1 Sui)
    gasbudget="100000000"  # Optional, defaults to 0.1 Sui
)
```

### Depositing Tokens into a Vault (Allowed for everyone)

#### Supported wallets (blake2b hashing required, since its a sui transaction):

- `ED25519`

```python
rfq_client.deposit_in_vault(
    vault="0x40923d059eae6ccbbb91ac9442b80b9bec8262122a5756d96021e34cf33f0b1d",
    amount="200000000000",
    coin_type="0x0000000000000000000000000000000000000000000000000000000000000002::sui::SUI",
    gasbudget="100000000"  # Optional, defaults to 0.1 Sui
)
```

### Withdrawing Tokens from a Vault (Only Vault Manager)

#### Supported wallets (blake2b hashing required, since its a sui transaction):

- `ED25519`

```python
rfq_client.withdraw_from_vault(
    vault="0x40923d059eae6ccbbb91ac9442b80b9bec8262122a5756d96021e34cf33f0b1d",
    amount="200000000000",
    coin_type="0x0000000000000000000000000000000000000000000000000000000000000002::sui::SUI",
    gasbudget="100000000"  # Optional, defaults to 0.1 Sui
)
```

### Updating Vault Manager (Only Vault Manager)

#### Supported wallets (blake2b hashing required, since its a sui transaction):

- `ED25519`

```python
rfq_client.update_vault_manager(
    vault="0x40923d059eae6ccbbb91ac9442b80b9bec8262122a5756d96021e34cf33f0b1d",
    new_manager="0xnew_manager_address",
    gasbudget="100000000"  # Optional, defaults to 0.1 Sui
)
```

### Updating Minimum Deposit Amount (Only Vault Manager)

#### Supported wallets (blake2b hashing required, since its a sui transaction):

- `ED25519`

```python
rfq_client.update_min_deposit_for_coin(
    vault="0x40923d059eae6ccbbb91ac9442b80b9bec8262122a5756d96021e34cf33f0b1d",
    coin_type="0x2::sui::SUI",
    min_amount="1000000",  # (scaled to supported coin decimals, eg. 1000000000 for 1 Sui)
    gasbudget="100000000"  # Optional, defaults to 0.1 Sui
)
```

### Getting Vault Balance for specified token

```python
balance = rfq_client.get_vault_coin_balance(
    vault="0x40923d059eae6ccbbb91ac9442b80b9bec8262122a5756d96021e34cf33f0b1d",
    coin_type="0x2::sui::SUI"
)
```

## API Reference

### Return Types

#### TransactionResult
A structured response from the SUI chain containing:
- `effects`: Transaction effects including status, gas used, and mutated objects
- `digest`: Transaction digest
- `transaction`: Transaction details
- `object_changes`: Changes to objects
- `events`: Transaction events

### Methods

#### `RFQClient(wallet: SuiWallet, url: str, rfq_contracts: RFQContracts)`

Initializes the RFQClient.

##### Parameters:

- `wallet` (SuiWallet): Instance of SuiWallet.
- `url` (str): RPC URL of the chain node.
- `rfq_contracts` (RFQContracts): Instance of RFQContracts.

##### Returns:
- `RFQClient`: Instance of RFQClient.

#### `create_quote(...) -> Quote`

Creates a quote instance.

##### Parameters:

- `vault` (str): On-chain vault object ID.
- `quote_id` (str): Unique quote ID.
- `taker` (str): Address of the receiver.
- `token_in_amount` (int): Amount of the input token ()
- `token_out_amount` (int): Amount of the output token (scaled to supported coin decimals, eg. 1000000000 for 1 Sui).
- `token_in_type` (str): On-chain token type of input coin. (scaled to supported coin decimals, eg. 1000000 for 1 USDC).
- `token_out_type` (str): On-chain token type of output coin.
- `created_at_utc_ms` (int, optional): Creation UTC timestamp in milliseconds (default: current time).
- `expires_at_utc_ms` (int, optional): Expiry UTC timestamp in milliseconds (default: 30 seconds after creation timestamp).

##### Returns:
- `Quote`: Instance of Quote class.

#### `create_and_sign_quote(...) -> Tuple[Quote, str]`

Creates and signs a quote.

##### Parameters:
Same as `create_quote`

##### Returns:
- `Tuple[Quote, str]`: Tuple containing Quote instance and base64 encoded signature.

#### `deposit_in_vault(vault: str, amount: str, coin_type: str, gasbudget: str = "100000000") -> Tuple[bool, TransactionResult]`

Deposits a token amount into the vault.

##### Parameters:
- `vault` (str): On-chain vault object ID.
- `amount` (str): Amount to deposit (scaled to supported coin decimals, eg. 1000000000 for 1 Sui).
- `coin_type` (str): On-chain token type.
- `gasbudget` (str, optional): Gas budget for transaction (default: "100000000", 0.1 Sui).

##### Returns:
- `Tuple[bool, TransactionResult]`: Success status and transaction result.

#### `withdraw_from_vault(vault: str, amount: str, coin_type: str, gasbudget: str = "100000000") -> Tuple[bool, TransactionResult]`

Withdraws a token amount from the vault (only vault manager).

##### Parameters:
- `vault` (str): On-chain vault object ID.
- `amount` (str): Amount to withdraw (scaled to supported coin decimals, eg. 1000000000 for 1 Sui).
- `coin_type` (str): On-chain token type.
- `gasbudget` (str, optional): Gas budget for transaction (default: "100000000", 0.1 Sui).

##### Returns:
- `Tuple[bool, TransactionResult]`: Success status and transaction result.

#### `create_vault(manager: str, gasbudget: str = "100000000") -> Tuple[bool, TransactionResult]`

Creates a new vault on bluefin RFQ protocol.

##### Parameters:
- `manager` (str): Address of the vault manager.
- `gasbudget` (str, optional): Gas budget for transaction (default: "100000000", 0.1 Sui).

##### Returns:
- `Tuple[bool, TransactionResult]`: Success status and transaction result.

#### `add_coin_support(vault: str, coin_type: str, min_amount: str, gasbudget: str = "100000000") -> Tuple[bool, TransactionResult]`

Adds support for a coin in the vault (only vault manager).

##### Parameters:
- `vault` (str): On-chain vault object ID.
- `coin_type` (str): On-chain token type.
- `min_amount` (str): Minimum deposit amount (scaled to supported coin decimals, eg. 1000000000 for 1 Sui).
- `gasbudget` (str, optional): Gas budget for transaction (default: "100000000", 0.1 Sui).

##### Returns:
- `Tuple[bool, TransactionResult]`: Success status and transaction result.

#### `update_vault_manager(vault: str, new_manager: str, gasbudget: str = "100000000") -> Tuple[bool, TransactionResult]`

Updates the vault manager (only current manager).

##### Parameters:
- `vault` (str): On-chain vault object ID.
- `new_manager` (str): Address of the new manager.
- `gasbudget` (str, optional): Gas budget for transaction (default: "100000000", 0.1 Sui).

##### Returns:
- `Tuple[bool, TransactionResult]`: Success status and transaction result.

#### `update_min_deposit_for_coin(vault: str, coin_type: str, min_amount: str, gasbudget: str = "100000000") -> Tuple[bool, TransactionResult]`

Updates minimum deposit amount for a coin (only vault manager).

##### Parameters:
- `vault` (str): On-chain vault object ID.
- `coin_type` (str): On-chain token type.
- `min_amount` (str): New minimum amount (scaled to supported coin decimals, eg. 1000000000 for 1 Sui).
- `gasbudget` (str, optional): Gas budget for transaction (default: "100000000", 0.1 Sui).

##### Returns:
- `Tuple[bool, TransactionResult]`: Success status and transaction result.

#### `get_vault_coin_balance(vault: str, coin_type: str) -> str`

Gets the balance of a specific coin in the vault.

##### Parameters:
- `vault` (str): On-chain vault object ID.
- `coin_type` (str): On-chain token type.

##### Returns:
- `str`: Balance of the coin ((scaled to supported coin decimals, eg. 1000000000 for 1 Sui)).

## Error Handling

The client may raise the following exceptions:
- `ValueError`: When required parameters are missing or invalid
- `Exception`: When transaction execution fails or other errors occur

## Contact

For issues and inquiries, please open a GitHub issue or contact Bluefin team.
