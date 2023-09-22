import requests
import json
import time

LOCKED_OBJECT_ERROR_CODE = (
    "Failed to sign transaction by a quorum of validators because of locked objects"
)


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
    Input:
      url: url of the node
      params: a list of arguments to be passed to function
      function_name: name of the function to call on sui
      function_library: name of the library/module in which the function exists
      userAddress: Address of the signer
      packageId: package id in which the module exists
      gasBudget(optional): gasBudget defaults to 100000000
      typeArguments (optional): type arguments if any in list format [your_arg_1]

    Output:
      Returns the request form serialised in bytes ready to be signed.

    """
    base_dict = {}
    base_dict["jsonrpc"] = "2.0"
    base_dict["id"] = 1689764924887
    base_dict["method"] = "unsafe_moveCall"
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

    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", url, headers=headers, data=payload)
    result = json.loads(response.text)
    return result["result"]["txBytes"]


def rpc_sui_executeTransactionBlock(url, txBytes, signature, maxRetries=5):
    """
    Execute the SUI call on sui chain
    Input:
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


def rpc_call_sui_function(url, params, method="suix_getCoins"):
    """
    for calling sui functions:
    Input:
      url: url of node
      params: arguments of function
      method(optional): the name of method in sui we want to call. defaults to suix_getCoins
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
    return result["result"]
