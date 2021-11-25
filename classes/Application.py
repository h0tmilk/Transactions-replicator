import json
import os
import sys

import requests_cache
import yaml

import eth_keyfile
import secrets

import requests
from eth_keyfile import load_keyfile
from sha3 import keccak_256

from web3 import Web3
from termcolor import colored

from classes.Config import Config


def confirmation(label, default="yes"):
    valid = {"yes": True, "y": True, "Y": True,
             "no": False, "n": False, "N": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(label + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Invalid input\n")


class Application:

    def __init__(self, config_path, accounts_path="./accounts/"):
        self.conf = Config(config_path)
        self.accounts_path = accounts_path
        self.accounts = {}
        self.transactions = {}
        requests_cache.install_cache("API_CACHE", backend="sqlite", expire_after=60)

    def create_accounts(self, number, path, password):
        for x in range(number):
            private_key = keccak_256(secrets.token_bytes(32)).digest()
            keyfile_content = eth_keyfile.create_keyfile_json(private_key, password.encode())
            address = keyfile_content["address"]

            keyfile = open(path + "/keyfile_" + address[:5] + ".json", "w")
            keyfile.write(json.dumps(keyfile_content, indent=4))
            keyfile.close()

    def load_accounts(self, password):
        for keyfile in os.listdir(self.accounts_path):
            keyfile_json = load_keyfile(self.accounts_path + keyfile)
            try:
                self.accounts['0x' + keyfile_json['address'].lower()] = \
                    eth_keyfile.decode_keyfile_json(keyfile_json, password.encode()).hex()
            except ValueError:
                raise ValueError("{} Incorrect password.".format(colored('[ERROR]', 'red')))

    def load_web3(self, blockchain):
        return Web3(Web3.HTTPProvider(self.conf.blockchains[blockchain]['web3_uri']))

    def get_gas_oracle(self, blockchain):
        url_api = self.conf.blockchains[blockchain]['api_url'] + "api"
        api_key = os.environ[self.conf.blockchains[blockchain]['api_token']]
        query = {
            'module': 'gastracker',
            'action': 'gasoracle',
            'apikey': api_key
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        }
        response = json.loads(requests.get(url_api, headers=headers, params=query).text)

        return response['result']

    def estimate_tx_fees(self, web3, blockchain, transaction, address_from):
        tx = {
            'from': web3.toChecksumAddress(address_from),
            'to': web3.toChecksumAddress(transaction['to']),
            'value': transaction['value'],
            'input': transaction['input']
        }

        gas_station = self.get_gas_oracle(blockchain)
        price = gas_station['SafeGasPrice']

        estimated_gas = web3.eth.estimate_gas(tx)
        estimated_fees = round(estimated_gas * float(web3.fromWei(web3.toWei(price, 'gwei'), 'ether')), 5)

        return {
            'estimated_gas': estimated_gas,
            'estimated_fees': estimated_fees,
            'price': price
        }

    def extract_transactions_from_address(self, address, blockchains):
        playbook = {}
        playbook_filename = 'playbooks/playbook_{}.yaml'.format(address[:8])
        for current_blockchain in blockchains:
            url_api = self.conf.blockchains[current_blockchain]['api_url'] + 'api'
            api_key = os.environ[self.conf.blockchains[current_blockchain]['api_token']]
            query = {
                'module': 'account',
                'action': 'txlist',
                'address': address,
                'startblock': '0',
                'endblock': '99999999',
                'sort': 'asc',
                'apikey': api_key,
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
            }
            response = json.loads(requests.get(url_api, headers=headers, params=query).text)

            playbook[current_blockchain] = list()
            for transaction in response["result"]:
                if transaction["from"].lower() == address.lower():
                    playbook[current_blockchain].append(transaction['hash'])
                    print('{} Written {} transactions on {} in {}'.format(
                        colored('[INFO]', 'magenta'),
                        address[:8],
                        current_blockchain,
                        playbook_filename
                    ))

        playbook_file = open(playbook_filename, "w")
        playbook_file.write(yaml.dump(playbook))
        playbook_file.close()

    def load_transactions(self, playbook):
        with open(playbook, "r") as stream:
            try:
                parsed_playbook = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        for blockchain in parsed_playbook:
            web3 = self.load_web3(blockchain)
            self.transactions[blockchain] = {}
            for transaction_hash in parsed_playbook[blockchain]:
                self.transactions[blockchain][transaction_hash] = web3.eth.get_transaction(transaction_hash)

    def farm(self, password, playbook, blockchains):
        self.load_accounts(password)
        self.load_transactions(playbook)

        for blockchain in blockchains:
            # Calculate fees
            web3 = self.load_web3(blockchain)
            total_fees = 0
            total_tx = 0
            for tx_hash, tx in self.transactions[blockchain].items():
                # Estimate total fees
                test_address = list(self.accounts.keys())[0] \
                    if web3.toChecksumAddress(list(self.accounts.keys())[0]) != tx['from'] \
                    else web3.toChecksumAddress(self.accounts[1])
                fees = self.estimate_tx_fees(web3, blockchain, tx, test_address)
                for address, private_key in self.accounts.items():
                    if web3.toChecksumAddress(address) != web3.toChecksumAddress(tx['from']):
                        total_fees += total_fees + fees['estimated_fees']
                        total_tx += 1

                confirm = confirmation('{} Replicate transaction {} on {} accounts for {} {} fees ({} {} each)'.format(
                    colored('[CONFIRM]', 'blue'),
                    str(tx_hash),
                    str(total_tx),
                    str(total_fees)[:7],
                    str(self.conf.blockchains[blockchain]['symbol']),
                    str(total_fees / total_tx)[:7],
                    str(self.conf.blockchains[blockchain]['symbol'])),
                    'no')

                if not confirm:
                    print('{} Skipped transaction {}.'.format(colored('[INFO]', 'magenta'), tx_hash))
                else:
                    # Then we go through the accounts to perform the transactions
                    for address in self.accounts:
                        if web3.toChecksumAddress(address) != web3.toChecksumAddress(tx['from']):
                            self.replicate_transaction(web3, blockchain, tx, address)

    def dispatch_currency(self, amount, from_address, blockchain, password):
        web3 = self.load_web3(blockchain)
        self.load_accounts(password)

        from_address = web3.toChecksumAddress(from_address)

        if from_address.lower() not in self.accounts:
            raise ValueError('{} {} is not in {}.'.format(
                colored('[ERROR]', 'red'),
                from_address,
                self.accounts_path
            ))

        nb_dest_addresses = len(self.accounts) - 1
        total_amount = str(nb_dest_addresses * amount)

        confirm = confirmation('{} {} {} will be sent to {} addresse(s)'.format(
            colored('[CONFIRM]', 'blue'),
            str(total_amount),
            self.conf.blockchains[blockchain]['symbol'],
            str(nb_dest_addresses)
        ), 'no')
        if not confirm:
            sys.exit('Cancelled')

        balance = web3.fromWei(web3.eth.get_balance(from_address), "ether")
        if balance <= amount:
            raise ValueError('{} Address {} has only {} {} and the operation needs at least {} {}'.format(
                colored('[ERROR]', 'red'),
                from_address,
                str(balance),
                self.conf.blockchains[blockchain]['symbol'],
                str(total_amount),
                self.conf.blockchains[blockchain]['symbol']
            ))

        gas_station = self.get_gas_oracle(blockchain)
        price = gas_station['SafeGasPrice']

        # Estimated gas fees with minimal transaction and then multiply by the amount of dest addresses
        tx = {
            'to': '0x0000000000000000000000000000000000007357',  # random address
            'value': web3.toWei(amount, 'ether')
        }
        estimated_gas = web3.eth.estimate_gas(tx)
        estimated_fees = round(estimated_gas * float(web3.fromWei(web3.toWei(price, 'gwei'), 'ether')), 5)
        estimated_total_fees = estimated_fees * nb_dest_addresses

        confirm = confirmation('{} The estimated total gas fees for the operation(s) is estimated at {} {}'.format(
            colored('[CONFIRM]', 'blue'), str(estimated_total_fees), str(self.conf.blockchains[blockchain]['symbol'])),
            'no')

        if not confirm:
            sys.exit('Cancelled')

        private_key = self.accounts[from_address.lower()]
        nonce = web3.eth.getTransactionCount(from_address)

        for address, key in self.accounts.items():
            if address != from_address.lower():
                tx = {
                    'nonce': nonce,
                    'to': web3.toChecksumAddress(address),
                    'value': web3.toWei(amount, 'ether'),
                    'gas': estimated_gas,
                    'gasPrice': web3.toWei(price, 'gwei')
                }
                signed_tx = web3.eth.account.sign_transaction(tx, private_key)
                tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
                nonce += 1
                print('{} {} ----- {} {} -----> {} : {}tx/{}'.format(
                    colored('[TX]', 'green'),
                    from_address[:8],
                    str(amount),
                    str(self.conf.blockchains[blockchain]['symbol']),
                    address[:8],
                    self.conf.blockchains[blockchain]['api_url'].replace('api-', ''),
                    str(tx_hash.hex())))

    def replicate_transaction(self, web3, blockchain, tx, address):
        private_key = self.accounts[address.lower()]
        nonce = web3.eth.getTransactionCount(web3.toChecksumAddress(address))
        fees = self.estimate_tx_fees(web3, blockchain, tx, address)

        transaction = {
            'nonce': nonce,
            'from': web3.toChecksumAddress(address),
            'to': tx['to'],
            'value': tx['value'],
            'data': tx['input'],
            'gas': fees['estimated_gas'],
            'gasPrice': web3.toWei(fees['price'], 'gwei')
        }

        signed_tx = web3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        print('{} Replicated transaction {} on {}: {}{}'.format(
            colored('[TX]', 'green'),
            str(tx['hash'].hex()),
            address[:8],
            self.conf.blockchains[blockchain]['api_url'].replace('api-', '')+'tx/',
            str(tx_hash.hex())))


