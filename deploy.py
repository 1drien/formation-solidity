from solcx import compile_standard
from solcx import install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

print("Installing solc...")
install_solc("0.6.0")
print("--------")
# Configure compile standards
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)

# Dump the compiled code to see the structure of the code
with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# For connecting to ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
chain_id = 1337
my_address = "0xa67778Fe7074Cb7aAbD863183bEaBbf079882dc4"
private_key = "0x2d366b891b65d9d2df2c74bae59bc1a6d1bd56e97a75f858feb69e04b17ca5de"
print(os.getenv("SOME_OTHER_VAR"))

# Create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# get the lastest transaction
nonce = w3.eth.get_transaction_count(my_address)

# buid a transaction
transaction = SimpleStorage.constructor().build_transaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce,
    }
)

# Signer la transaction avec la clé privée
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# Déployer le contrat
print("deploying contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("deployed")
# contract_addr = tx_receipt.contractAddressprint(
#   f"Contract is deployed to {contract_addr}"
# )

# Puisque le contrat intelligent est déployé, nous pouvons fournir l'adresse du contrat et l'abi pour créer le contrat intelligent ("simple_storage").
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# Call -> simulate
# transact -> actually make a state change

# intital values of favourite nuber
print(simple_storage.functions.retrieve().call())
print("updating contract...")

store_transaction = simple_storage.functions.store(15).build_transaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce + 1,
    }
)
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("updated")
print(simple_storage.functions.retrieve().call())
