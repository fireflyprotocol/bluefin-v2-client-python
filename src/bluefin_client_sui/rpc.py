import requests
import json


def rpc_unsafe_moveCall(
    url,
    params,
    function_name: str,
    function_library: str,
    userAddress,
    packageId,
    gasBudget=100000000,
):
    base_dict = {}
    base_dict["jsonrpc"] = "2.0"
    base_dict["id"] = 1689764924887
    base_dict["method"] = "unsafe_moveCall"
    base_dict["params"] = []
    base_dict["params"].extend(
        [userAddress, packageId, function_library, function_name]
    )
    base_dict["params"].append([])
    base_dict["params"].append(params)

    base_dict["params"].append(None)
    base_dict["params"].append(str(gasBudget))

    payload = json.dumps(base_dict)

    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", url, headers=headers, data=payload)
    result = json.loads(response.text)
    return result["result"]["txBytes"]


def rpc_sui_executeTransactionBlock(url, txBytes, signature):
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
    response = requests.request("POST", url, headers=headers, data=payload)
    result = json.loads(response.text)
    return result


def rpc_call_sui_function(url, params, method="suix_getCoins"):
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


"""

payload = json.dumps({
  "jsonrpc": "2.0",
  "id": 5,
  "method": "sui_executeTransactionBlock",
  "params": [
    "AAADAQGPzuAZV5krLKJWD1WUXOjk7Guz2vki2pBMZJ6CXkRf1XLGgQAAAAAAAQAgH/qFdX+Vzs7ShiLTDkGkUsiFFt9TRQyxkTgS3YKNWWgAEOgDAAAAAAAAAAAAAAAAAAABAF82iNaL7Cly31h0P767ErFoKbQb8bxQeNNRAJDvbPWOC21hcmdpbl9iYW5rEndpdGhkcmF3X2Zyb21fYmFuawADAQAAAQEAAQIAH/qFdX+Vzs7ShiLTDkGkUsiFFt9TRQyxkTgS3YKNWWgBWiybg/9fRf7zXUmsdBU3umIFeucEZNWeMGzlLttPf86tHg8AAAAAACA3qZfzxP1+yVILtVkJ6LdfZvkF7gK877AJco9Xook9Th/6hXV/lc7O0oYi0w5BpFLIhRbfU0UMsZE4Et2CjVlo6AMAAAAAAAAA4fUFAAAAAAA=",
    [
      "ANyIBWjL6U9T6qBoWWTc18qzVViytirDmwX+dOEqd77dibe0tgLcziDZpe3XoTRVbBJGUV9TIHCN2C21aNvUTA/JFlIyQTT87zRFBPBubLG+G22kP5UDgk3kIg8JPeUiBw=="
    ],
    {
      "showInput": True,
      "showEffects": True,
      "showEvents": True,
      "showObjectChanges": True
    },
    "WaitForLocalExecution"
  ]
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)


"""


"""
url = "https://fullnode.testnet.sui.io:443"

payload = json.dumps({
  "jsonrpc": "2.0",
  "id": 1689764924887,
  "method": "unsafe_moveCall",
  "params": [
    "0x1ffa85757f95ceced28622d30e41a452c88516df53450cb1913812dd828d5968",
    "0x5f3688d68bec2972df58743fbebb12b16829b41bf1bc5078d3510090ef6cf58e",
    "margin_bank",
    "withdraw_from_bank",
    [],
    [
      "0x8fcee01957992b2ca2560f55945ce8e4ec6bb3daf922da904c649e825e445fd5",
      "0x1ffa85757f95ceced28622d30e41a452c88516df53450cb1913812dd828d5968",
      "1000"
    ],
    "0x5a2c9b83ff5f45fef35d49ac741537ba62057ae70464d59e306ce52edb4f7fce",
    "100000000"
  ]
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
"""
