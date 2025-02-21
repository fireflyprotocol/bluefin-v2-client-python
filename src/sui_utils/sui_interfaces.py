from typing import Any


class GasUsed:
    def __init__(self, gas_used: dict):
        self.computation_cost = gas_used.get("computationCost")
        self.storage_cost = gas_used.get("storageCost")
        self.storage_rebate = gas_used.get("storageRebate")
        self.non_refundable_storage_fee = gas_used.get("nonRefundableStorageFee")

class Owner:
    def __init__(self, owner: dict):
        self.address_owner = owner.get("AddressOwner")
        self.object_owner = owner.get("ObjectOwner")

class Reference:
    def __init__(self, reference: dict):
        self.object_id = reference.get("objectId")
        self.version = reference.get("version")
        self.digest = reference.get("digest")

class MutatedObject:
    def __init__(self, mutated: dict):
        self.owner = Owner(mutated.get("owner"))
        self.reference = Reference(mutated.get("reference"))

class GasObject:
    def __init__(self, gas_object: dict):
        self.owner = Owner(gas_object.get("owner"))
        self.reference = Reference(gas_object.get("reference"))

class Effects:
    def __init__(self, effects: dict):
        self.message_version = effects.get("messageVersion")
        self.status = effects.get("status").get("status")
        self.executed_epoch = effects.get("executedEpoch")
        self.gas_used = GasUsed(effects.get("gasUsed"))
        self.transaction_digest = effects.get("transactionDigest")
        self.mutated = [MutatedObject(m) for m in effects.get("mutated", [])]
        self.gas_object = GasObject(effects.get("gasObject"))
        self.events_digest = effects.get("eventsDigest")

class TransactionResult:
    def __init__(self, result: dict):
        self.digest = result.get("digest")
        self.transaction = result.get("transaction")
        self.raw_transaction = result.get("rawTransaction")
        self.effects = Effects(result.get("effects"))
        self.object_changes = result.get("objectChanges")

    def __repr__(self):
        return f"TransactionResult(digest={self.digest}, status={self.effects.status}, transaction_digest={self.effects.transaction_digest})"

class CoinMetadata:
    def __init__(self, metadata: dict):
        self.decimals = metadata.get("decimals")
        self.name = metadata.get("name")
        self.symbol = metadata.get("symbol")
        self.description = metadata.get("description")
        self.icon_url = metadata.get("iconUrl")
        self.id = metadata.get("id")

    def __repr__(self):
        return f"CoinMetadata(name={self.name}, symbol={self.symbol}, decimals={self.decimals})"

class Coin:
    def __init__(self, coin_data: dict):
        self.coin_type : str = coin_data.get("coinType")
        self.coin_object_id : str= coin_data.get("coinObjectId")
        self.version : str = coin_data.get("version")
        self.digest: str = coin_data.get("digest")
        self.balance : str = coin_data.get("balance")
        self.previous_transaction : str = coin_data.get("previousTransaction")

    def __repr__(self):
        return f"Coin(coin_type={self.coin_type}, coin_object_id={self.coin_object_id}, balance={self.balance})"

class NextCursor:
    def __init__(self, cursor: dict):
        self.tx_digest = cursor.get("txDigest")
        self.event_seq = cursor.get("eventSeq")

    def __repr__(self):
        return f"NextCursor(tx_digest={self.tx_digest}, event_seq={self.event_seq})"

class SuiGetResponse:
    def __init__(self, response: dict):
        self.raw : dict = response
        self.data : list[Any] = response.get("data", [])
        next_cursor = response.get("nextCursor")
        if isinstance(next_cursor, dict):
            self.next_cursor : NextCursor = NextCursor(next_cursor)
        else:
            self.next_cursor: str = next_cursor
        self.has_next_page: bool = response.get("hasNextPage",False)

    def __repr__(self):
        return f"CoinResponse(data={self.data}, next_cursor={self.next_cursor}, has_next_page={self.has_next_page})"
