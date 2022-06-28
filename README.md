# Transactions replicator (EVM-compatible chains))
Python tool to replicate transactions from a given address on any web3 compatible network. This can be used for example to farm 
existing transactions on tokenless Dapps to hunt for airdrops.

**This tool is working but is still in development. Use with caution.**

Next upcoming changes :
- Exceptions handling improvements
- Functions documentation
- Optimisation review

## How to use
Complete the config file as you wish with network informations. Example :
```yaml
blockchains:
  ethereum_ropsten:
      type: testnet
      web3_uri: https://ropsten.infura.io/v3/<infura_token>
      api_url: https://api-ropsten.etherscan.io/
      api_token: ETH_ROP_TOKEN # Name of the env variable containing the token
      symbol: ETH
```

### Create accounts
You can create several accounts (json keystore files ptected by password) with the *create_accounts* module.

Usage :
```bash
airdrop-autofarmer.py create_accounts [-h] -n NUMBER [-p PASSWORD] [-d DIRECTORY]

optional arguments:
  -h, --help            show this help message and exit
  -n NUMBER, --number NUMBER
                        Number of accounts to create.
  -p PASSWORD, --password PASSWORD
                        Password for keyfiles.
  -d DIRECTORY, --directory DIRECTORY
                        Directory where keyfiles will be generated.
```


Exemple :
```bash
python airdrop-autofarmer.py create_accounts -n 5 -d ./accounts -p 'password'
```

### Extract transactions from address
You may want to extract transactions from a "model" address you used to perform transactions you want to replicate.
You can do it with the *extract_transactions* module.

Usage :
````bash
airdrop-autofarmer.py extract_transactions [-h] -a ADDRESS -b BLOCKCHAINS

optional arguments:
  -h, --help            show this help message and exit
  -a ADDRESS, --address ADDRESS
                        Address from which transaction have to be extracted.
  -b BLOCKCHAINS, --blockchains BLOCKCHAINS
                        Blockchains names from which transactions have to be extracted (see config file), separated by commas.

````


Example :
```bash
python airdrop-autofarmer.py extract_transactions -a 0x50Dd138D8E6829C880BCf17BA78D701678608bE1 -b polygon_mainnet
```

### Send crypto to several accounts
You can send native blockchain token to all the addresses stored in the keyfiles folder.
The sender address must have its keyfile in the keyfiles folder.

Usage :
```bash
airdrop-autofarmer.py dispatch_currency [-h] -a AMOUNT -f FROM_ADDRESS -b BLOCKCHAIN -p PASSWORD [-k KEYS_DIR]

optional arguments:
  -h, --help            show this help message and exit
  -a AMOUNT, --amount AMOUNT
                        Amount of tokens to send to each address.
  -f FROM_ADDRESS, --from_address FROM_ADDRESS
                        Address which will send tokens.
  -b BLOCKCHAIN, --blockchain BLOCKCHAIN
                        Blockchain name where transactions will be made (see config file).
  -p PASSWORD, --password PASSWORD
                        Password of sender address keyfile.
  -k KEYS_DIR, --keys_dir KEYS_DIR
                        Directory where keyfiles are located.
```

Example (send 2 ethers from 0x56469 to all the addresses stored in the *./accounts* folder) :
```bash
python airdrop-autofarmer.py dispatch_currency -a 2 -b ethereum_ropsten -f 0x56469f4af31ad9d9401316a34b3b1a01cfb1b321 -p "password" -k ./accounts
```

### Replicate
Once your accounts have enough cryptos, you can use the *replicate* module to copy the transactions from the generated playbook of your choice (see *extract_transactions*) with all the accounts from the keystore folder.

Usage :
```bash
airdrop-autofarmer.py replicate [-h] -p PASSWORD -b BLOCKCHAINS -P PLAYBOOK [-k KEYS_DIR]

optional arguments:
  -h, --help            show this help message and exit
  -p PASSWORD, --password PASSWORD
                        Password of keyfiles.
  -b BLOCKCHAINS, --blockchains BLOCKCHAINS
                        Blockchain names from which transactions have to be extracted (see config file), separated by commas.
  -P PLAYBOOK, --playbook PLAYBOOK
                        Playbook file containing transactions and blockchains (generated with extract_transactions function.
  -k KEYS_DIR, --keys_dir KEYS_DIR
                        Directory where keyfiles are located.
```

Example :
```bash
python airdrop-autofarmer.py farm -p "password" -b ethereum_ropsten -P ./playbooks/playbook_0xd98A4e.yaml -f 0x56469f4af31ad9d9401316a34b3b1a01cfb1b321
```
