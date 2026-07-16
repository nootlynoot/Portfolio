import json, base64
from umbral import PublicKey, Capsule, reencrypt
from umbral.key_frag import KeyFrag

def b64d(s): 
    return base64.b64decode(s.encode("utf-8"))

def b64e(b: bytes) -> str:
    return base64.b64encode(b).decode("utf-8")

owner = json.load(open("owner_state.json", "r"))
retrieved = json.load(open("retrieved.json", "r"))
owner_pk = PublicKey.from_bytes(b64d(owner["owner_pk_b64"]))
recipient_pk = PublicKey.from_bytes(b64d(owner["recipient_pk_b64"]))
verifying_pk = PublicKey.from_bytes(b64d(owner["verifier_pk_b64"]))
capsule = Capsule.from_bytes(b64d(retrieved["capsule_b64"]))

kfrags = [KeyFrag.from_bytes(b64d(x)) for x in owner["kfrags_b64"]]
threshold = int(owner["threshold"])

verified_kfrags = []
for k in kfrags:
    vk = k.verify(verifying_pk, owner_pk, recipient_pk)
    verified_kfrags.append(vk)

cfrags = [reencrypt(capsule, vk) for vk in verified_kfrags[:threshold]]
print(f"Generated {len(cfrags)} cfrags.")

out = {
    "cid": retrieved.get("cid"),
    "assetId": retrieved.get("assetId"),
    "cfrags_b64": [b64e(bytes(cf)) for cf in cfrags]
}

with open("cfrags.json", "w") as f:
    json.dump(out, f, indent=2)