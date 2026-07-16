import time

from umbral import PublicKey, SecretKey, encrypt, generate_kfrags, Signer
from eth_utils import keccak
from eth_account import Account
import base64
import requests
import json, os
from web3 import Web3
import json
from pathlib import Path

broadcast = json.load(open("broadcast/DeployPolicy.s.sol/31337/run-latest.json"))
CONTRACT_ADDR = Web3.to_checksum_address(broadcast["transactions"][0]["contractAddress"])
print("Using contract:", CONTRACT_ADDR)

OWNER_ADDR = os.environ["OWNER_ADDR"]
RECIPIENT_ADDR = os.environ["RECIPIENT_ADDR"]
CONTRACT_ADDR = Web3.to_checksum_address(os.environ["CONTRACT_ADDR"])


owner_sk = SecretKey.random()
owner_pk = owner_sk.public_key()

recipient_sk = SecretKey.random()
recipient_pk = recipient_sk.public_key()

owner_pk_bytes = base64.b64encode(bytes(owner_pk)).decode("utf-8")
recipient_pk_bytes = base64.b64encode(bytes(recipient_pk)).decode("utf-8")

owner_account = Account.from_key(OWNER_ADDR)
recipient_account = Account.from_key(RECIPIENT_ADDR)

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))


ABI = json.load(open("out/PolicyRegistry.sol/PolicyRegistry.json"))["abi"]

contract = w3.eth.contract(address=CONTRACT_ADDR, abi=ABI)

def to_bytes(x):
    for name in ("to_bytes", "to_secret_bytes", "__bytes__"):
        fn = getattr(x, name, None)
        if callable(fn):
            try:
                b = fn()
                if isinstance(b, (bytes, bytearray)):
                    return bytes(b)
            except TypeError:
                pass
    return bytes(x)

def register_account(account, public_key):
    tx =  contract.functions.registerAccount(public_key).build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas": contract.functions.registerAccount(public_key).estimate_gas({"from": account.address}),
        "gasPrice": w3.eth.gas_price
    })
    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    return w3.eth.wait_for_transaction_receipt(tx_hash)

recipt = register_account(owner_account, owner_pk_bytes)
recipt = register_account(recipient_account, recipient_pk_bytes)

stored_owner = contract.functions.accounts(owner_account.address).call()
stored_recipient = contract.functions.accounts(recipient_account.address).call()

plaintext = bytes("helloooooooooo", "utf-8")
capsule, ciphertext = encrypt(owner_pk, plaintext)

capsule_bytes = bytes(capsule)
capsule_hash = keccak(capsule_bytes)

def add_to_ipfs(payload):
    url = "http://127.0.0.1:5001/api/v0/add"
    files ={
        'file': ('data.json', json.dumps(payload))
    }
    r = requests.post(url, files=files)
    r.raise_for_status()
    return r.json()['Hash']

def pin_cid(cid):
    r = requests.post(f"http://127.0.0.1:5001/api/v0/pin/add?arg={cid}")
    r.raise_for_status()
    return r.json()

payload = {
    "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
    "capsule": base64.b64encode(bytes(capsule)).decode(),
    "version": 1,
    "algorithm": "pyumbral"
}

cid = add_to_ipfs(payload)

print(f"CID: {cid}")
pin_cid(cid)

capsule_bytes_32 = capsule_hash[:32]

fn = contract.functions.registerAsset(
    recipient_account.address,
    capsule_bytes_32,
    cid
)

tx = contract.functions.registerAsset(
    recipient_account.address,
    capsule_bytes_32,
    cid
).build_transaction({
    "from": owner_account.address,
    "nonce": w3.eth.get_transaction_count(owner_account.address),
    "gas": fn.estimate_gas({"from": owner_account.address}),
    "gasPrice": w3.eth.gas_price,
})
signed  = owner_account.sign_transaction(tx)
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("registerAsset status:", receipt.status)
asset_id = contract.events.AssetRegistered().process_receipt(receipt)[0]["args"]["assetId"]
print(f"Asset registered. assetId = {asset_id}")

asset_id = contract.events.AssetRegistered().process_receipt(receipt)[0]["args"]["assetId"]
json.dump({"assetId": asset_id}, open("chain_state.json", "w"), indent=2)
print(f"Asset registered on-chain. assetId = {asset_id}")

state = {
    "cid": cid,
    "capsule_hash": "0x" + capsule_hash.hex(),
    "owner_pk_b64": owner_pk_bytes,
    "recipient_sk_b64": base64.b64encode(to_bytes(recipient_sk)).decode(),
    "recipient_pk_b64": recipient_pk_bytes,
}
json.dump(state, open("owner_state.json", "w"), indent=2)

print("Waiting for recipient to request access...")
event_filter = contract.events.AccessRequested.create_filter(
    from_block="latest",
    argument_filters={"assetId": asset_id}
)


while True:
    for event in event_filter.get_new_entries():
        recipient_addr = event["args"]["recipient"]
        print(f"Access requested by {recipient_addr}. Generating kfrags")

        stored = contract.functions.accounts(recipient_addr).call()
        recipient_pk_chain = PublicKey.from_bytes(base64.b64decode(stored[1]))

        signer = Signer(owner_sk)
        verifier = signer.verifying_key()

        kfrags = generate_kfrags(
            delegating_sk=owner_sk,
            receiving_pk=recipient_pk_chain,
            signer=signer,
            threshold=5,
            shares=10
        )

        state.update({
            "verifier_pk_b64": base64.b64encode(bytes(verifier)).decode(),
            "kfrags_b64": [base64.b64encode(bytes(k)).decode() for k in kfrags],
            "threshold": 5
        })
        json.dump(state, open("owner_state.json", "w"), indent=2)
        print("Kfrags generated. owner_state.json updated.")
        exit(0)

    time.sleep(2)
    


