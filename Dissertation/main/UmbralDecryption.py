import json, base64
from umbral import SecretKey, PublicKey, Capsule, decrypt_reencrypted, CapsuleFrag

def b64d(s): 
    return base64.b64decode(s.encode("utf-8"))

owner = json.load(open("owner_state.json", "r"))
retrieved = json.load(open("retrieved.json", "r"))
cfrags_file = json.load(open("cfrags.json", "r"))

owner_pk = PublicKey.from_bytes(b64d(owner["owner_pk_b64"]))
verifying_pk = PublicKey.from_bytes(b64d(owner["verifier_pk_b64"])) 
recipient_sk = SecretKey.from_bytes(b64d(owner["recipient_sk_b64"]))
recipient_pk = recipient_sk.public_key()    

ciphertext = b64d(retrieved["ciphertext_b64"])
capsule = Capsule.from_bytes(b64d(retrieved["capsule_b64"]))

cfrags = []
for x in cfrags_file["cfrags_b64"]:
    cf = CapsuleFrag.from_bytes(b64d(x))
    verified = cf.verify(capsule, verifying_pk, owner_pk, recipient_pk)
    cfrags.append(verified)

plaintext = decrypt_reencrypted(
    recipient_sk,
    owner_pk,
    capsule,
    cfrags,
    ciphertext
)

print("Plaintext:", plaintext)