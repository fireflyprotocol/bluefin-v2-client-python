import requests
import json
import time
from .sui_interfaces import *

LOCKED_OBJECT_ERROR_CODE = (
    "Failed to sign transaction by a quorum of validators because of locked objects"
)

def rpc_sui_getTransactionBytes(url: str, json_rpc_payload: str) -> str:
    """
    gets transaction bytes with the given json rpc payload to get txBytes.

    Inputs:
      url (str): URL of the node.
      payload (str): JSON payload to send in the request.

    Output:
      str: The txBytes.
    """
    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", url, headers=headers, data=json_rpc_payload)
    responseJson = json.loads(response.text)
    if "result" not in responseJson or "txBytes" not in responseJson["result"]:
        raise Exception(f"Failed to create transaction bytes due to: {responseJson}")
    return responseJson["result"]["txBytes"]

def rpc_unsafe_moveCall(
    url: str,
    params: list,
    function_name: str,
    function_library: str,
    userAddress: str,
    packageId: str,
    gasBudget: int = 100000000,
    typeArguments: list = [],
):
    """
    Does the RPC call to SUI chain
    Inputs:
      url: url of the node
      params: a list of arguments to be passed to function
      function_name: name of the function to call on sui
      function_library: name of the library/module in which the function exists
      userAddress: Address of the signer
      packageId: package id in which the module exists
      gasBudget(optional): gasBudget defaults to 100000000
      typeArguments (optional): type arguments if any in list format [your_arg_1]

    Output:
      Returns the request form serialized in bytes ready to be signed.

    """
    base_dict = {}
    base_dict["jsonrpc"] = "2.0"
    base_dict["method"] = "unsafe_moveCall"
    base_dict["id"] = 1
    base_dict["params"] = []
    base_dict["params"].extend(
        [userAddress, packageId, function_library, function_name]
    )

    # Optional type arguments for wormhole related calls
    base_dict["params"].append(typeArguments)
    base_dict["params"].append(params)

    base_dict["params"].append(None)
    base_dict["params"].append(str(gasBudget))

    payload = json.dumps(base_dict)

    return rpc_sui_getTransactionBytes(url, payload)

def rpc_sui_executeTransactionBlock(url: str, txBytes: str, signature: str , maxRetries=5) -> any:
    """
    Execute the SUI call on sui chain
    Inputs:
      url: url of the node
      txBytes: the call in serialised form
      signature: txBytes signed by signer

    Output:
      result of transaction


    """
    base_dict = {}
    base_dict["jsonrpc"] = "2.0"
    base_dict["id"] = 5
    base_dict["method"] = "sui_executeTransactionBlock"
    base_dict["params"] = []
    base_dict["params"].append(txBytes)
    base_dict["params"].append([signature])

    outputTypeDict = {
        "showInput": True,
        "showEffects": True,
        "showEvents": True,
        "showObjectChanges": True,
    }
    base_dict["params"].append(outputTypeDict)
    base_dict["params"].append("WaitForLocalExecution")
    payload = json.dumps(base_dict)

    headers = {"Content-Type": "application/json"}

    for i in range(0, maxRetries):
        response = requests.request("POST", url, headers=headers, data=payload)
        result = json.loads(response.text)
        if "error" in result:
            if result["error"]["message"].find(LOCKED_OBJECT_ERROR_CODE) == -1:
                return result
        else:
            return result

        time.sleep(1)
    return result

def rpc_sui_getDynamicFieldObject(url:str, parentObjectId: str, fieldName: str,fieldSuiObjectType:str, maxRetries=5):
    """
    Fetches the on-chain dynamic field object corresponding to specified input params
    Inputs:
      url: url of the sui chain node
      parentObjectId: id of the parent object for which dynamic field needs to be queried
      fieldName: name of the dynamic field
      fieldSuiObjectType: sui object type for the dynamic field name (eg. for string use , `0x1::string::String`)

    Output:
      sui result object for the dynamic field
    """
    base_dict = {}
    base_dict["jsonrpc"] = "2.0"
    base_dict["id"] = 5
    base_dict["method"] = "suix_getDynamicFieldObject"
    base_dict["params"] = []
    base_dict["params"].append(parentObjectId)
    base_dict["params"].append({
         "type": fieldSuiObjectType,
         "value": fieldName
    })
    payload = json.dumps(base_dict)

    headers = {"Content-Type": "application/json"}

    for i in range(0, maxRetries):
        response = requests.request("POST", url, headers=headers, data=payload)
        result = json.loads(response.text)
        if "error" in result:
            if result["error"]["message"].find(LOCKED_OBJECT_ERROR_CODE) == -1:
                return result
        else:
            return result

        time.sleep(1)
    return result

def rpc_call_sui_function(url: str, params: list[Any], method: str = "suix_getCoins") -> SuiGetResponse:
    """
    for calling sui chain functions:
    Inputs:
      url: url of node
      params: arguments of function
      method(optional): the name of method in sui we want to call. defaults to suix_getCoins

    Output:
      SuiGetResponse: The response containing data.
    """
    base_dict = {}
    base_dict["jsonrpc"] = "2.0"
    base_dict["id"] = 1
    base_dict["method"] = method
    base_dict["params"] = params
    payload = json.dumps(base_dict)

    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", url, headers=headers, data=payload)
    result = json.loads(response.text)
    return SuiGetResponse(result["result"])

def rpc_sui_createSplitCoinsTransaction(owner: str, primary_coin_id: str = None, split_amounts: list[str] = [], url: str = None, gas_budget: int = 100000000):
    """
    Creates a transaction to split a coin into smaller amounts as specified in split_amounts.
    
    Inputs:
      owner: Address of the owner.
      primary_coin_id: ID of the primary coin to split.
      split_amounts: List of amounts to split into (as big number strings scaled in coin decimals supported by the coin). Eg: 1000000000 for 1 SUI.
      url: URL of the node.
      gas_budget: Gas budget for the transaction (default: 100000000).

    Output:
      transaction bytes of the split operation.
    """
    try:
        # Check if split_amounts contains only number strings
        for amount in split_amounts:
            if not amount.isdigit():
                raise ValueError(f"Invalid amount in split_amounts: {amount}")
            
        base_dict = {
            "jsonrpc": "2.0",
            "method": "unsafe_splitCoin",
            "id": 1,
            "params": [
                owner,
                primary_coin_id,
                split_amounts,
                None,  # gas object ID, let node pick one
                str(gas_budget)
            ]
        }

        payload = json.dumps(base_dict)

        tx_bytes = rpc_sui_getTransactionBytes(url, payload)
        return tx_bytes
    except Exception as e:
        raise Exception(f"Failed to split coins, Exception: {e}")

def rpc_sui_createMergeCoinsTransaction(url: str, primary_coin_id: str, coin_id: str, userAddress: str, gasBudget: int = 100000000) -> str:
    """
    Creates a transaction to merge a coin into a primary coin.

    Inputs:
      url (str): URL of the node.
      primary_coin_id (str): The ID of the primary coin to merge into.
      coin_id (str): The ID of the coin to merge.
      userAddress (str): Address of the user.
      gasBudget (int): Gas budget for the transaction.

    Output:
      str: The transaction bytes.
    """
    try:
        base_dict = {
            "jsonrpc": "2.0",
            "method": "unsafe_mergeCoins",
            "id": 1,
            "params": [userAddress, primary_coin_id, coin_id, None, str(gasBudget)]
        }

        payload = json.dumps(base_dict)
        return rpc_sui_getTransactionBytes(url, payload)
    except Exception as e:
        raise Exception(f"Failed to merge coins, Exception: {e}")

def get_coin_balance(user_address: str = None, coin_type: str = "0x::sui::SUI", url: str = None) -> str:
    """
    Gets the balance of the specified coin type for the user.
    Input:
        user_address (str): The address of the user.
        coin_type (str): The type of the coin.
        url (str): The URL of the SUI node.
    Output:
        str: The balance of the coin scaled to coin decimals supported by the coin. Eg: 1000000000 for 1 SUI.
    """
    try:
        callArgs = []
        callArgs.append(user_address)
        callArgs.append(coin_type)
        result = rpc_call_sui_function(
            url, callArgs, method="suix_getBalance"
        )
        return result.raw["totalBalance"]
    except Exception as e:
        raise (Exception("Failed to get coin balance, Exception: {}".format(e)))


def get_coin_having_balance(user_address: str = None, coin_type: str = "0x::sui::SUI", balance: str = None , url: str = None, exact_match: bool = False) -> str:
    """
    Gets the coin having the specified balance.
    Input:
        user_address (str): The address of the user.
        coin_type (str): The type of the coin.
        balance (str): The balance of the coin scaled to coin decimals supported by the coin. Eg: 1000000000 for 1 SUI.
        url (str): The URL of the SUI node.
        exact_match (bool): Whether to find an exact match or a coin with balance greater than or equal to the specified balance.
    Output:
        str: The ID of the coin.
    """
    coin_list = get_coins_with_type(user_address, coin_type, url)
    for coin in coin_list:
        if exact_match:
                if int(coin.balance) == int(balance):
                    return coin.coin_object_id
        elif int(coin.balance) >= int(balance):
            return coin.coin_object_id
    raise Exception(
        "Not enough balance available in single coin, please merge your coins"
    )

def get_coin_metadata(url: str, coin_type: str) -> CoinMetadata:
    """
    Fetches the metadata for the specified coin type.

    Input:
      url (str): URL of the node.
      coin_type (str): The coin type to fetch metadata for.

    Output:
      CoinMetadata: The metadata of the coin.
    """
    base_dict = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "suix_getCoinMetadata",
        "params": [coin_type]
    }

    payload = json.dumps(base_dict)
    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", url, headers=headers, data=payload)
    responseJson = json.loads(response.text)
    if "result" not in responseJson:
        raise Exception(f"Failed to fetch coin metadata due to: {responseJson}")
    return CoinMetadata(responseJson["result"])

def get_coins_with_type(user_address: str = None, coin_type: str = "0x::sui::SUI", url: str = None) -> list[Coin]:
    """
    Returns the list of the coins of type tokenType owned by user.

    Input:
      user_address (str): The address of the user.
      coin_type (str): The coin type to fetch.
      url (str): The URL of the node.

    Output:
      list[Coin]: A list of Coin objects.
    """
    try:
        coins = []
        cursor = None
        while True:
            callArgs = [user_address, coin_type]
            if cursor:
                callArgs.append(cursor)
            response = rpc_call_sui_function(url, callArgs, method="suix_getCoins")
            coins.extend([Coin(element) for element in response.data])
            if not response.has_next_page:
                break
            cursor = response.next_cursor
        return coins
    except Exception as e:
        raise Exception(f"Failed to get coins, Exception: {e}")