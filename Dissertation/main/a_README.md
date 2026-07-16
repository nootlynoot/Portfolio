## Execution order
1.
run in a bash terminal: ipfs daemon 

2.
run in a bash terminal: anvil

3.
run in a bash terminal:
forge script script/DeployPolicy.s.sol:DeployPolicy \
  --rpc-url http://127.0.0.1:8545 \
  --broadcast \
  --private-key=(get from account 0 private key under anvil accounts) 

4.
run in a bash terminal:
export CONTRACT_ADDR=$(cat broadcast/DeployPolicy.s.sol/31337/run-latest.json | python -c "import json,sys; data=json.load(sys.stdin); print(data['transactions'][0]['contractAddress'])")


There should be 4 bash terminals, one for IPFS, one for Anvil, and 2 for the scripts

5.
run UmbralDecryption in a script terminal

6.
run zFetchData in the other script terminal

7.
when UmbralDecryption has finished generating kfrags, run ProxyFunctions

8.
Finally run UmbralDecryption