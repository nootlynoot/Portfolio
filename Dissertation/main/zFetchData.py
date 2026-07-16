import json, os, requests, time
from web3 import Web3
from eth_account import Account
import json
from pathlib import Path


broadcast = json.load(open("broadcast/DeployPolicy.s.sol/31337/run-latest.json"))
CONTRACT_ADDR = Web3.to_checksum_address(broadcast["transactions"][0]["contractAddress"])
IPFS_GATEWAY  = "http://127.0.0.1:8080"

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
ABI = json.load(open("out/PolicyRegistry.sol/PolicyRegistry.json"))["abi"]
recipient_account = Account.from_key(os.environ["RECIPIENT_ADDR"])
contract = w3.eth.contract(address=CONTRACT_ADDR, abi=ABI)
chain_state = json.load(open("chain_state.json"))
asset_id = chain_state["assetId"]

print("Requesting access on-chain")
tx = contract.functions.requestAccess(asset_id).build_transaction({
    "from": recipient_account.address,
    "nonce": w3.eth.get_transaction_count(recipient_account.address),
    "gas": contract.functions.requestAccess(asset_id).estimate_gas({"from": recipient_account.address}),
    "gasPrice": w3.eth.gas_price,
})
signed = recipient_account.sign_transaction(tx)
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
w3.eth.wait_for_transaction_receipt(tx_hash)

print("Owner generating kfrags")

asset = contract.functions.assets(asset_id).call()
print("asset_id:", asset_id)
print("assetCount:", contract.functions.assetCount().call())
cid = asset[3]
print(f"CID from chain: {cid}")

res = requests.get(f"{IPFS_GATEWAY}/ipfs/{cid}")
res.raise_for_status()
data = res.json()

json.dump({
    "assetId": asset_id,
    "cid": cid,
    "ciphertext_b64": data["ciphertext"],
    "capsule_b64": data["capsule"],
}, open("retrieved.json", "w"), indent=2)