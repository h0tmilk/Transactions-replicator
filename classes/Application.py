import json
import os
import sys

import yaml
from colorama import Fore, Back, Style

import eth_keyfile
import secrets

import requests
from eth_keyfile import load_keyfile
from sha3 import keccak_256

from web3 import Web3
from web3.gas_strategies.time_based import medium_gas_price_strategy

from classes.Config import Config


class Application:

    def __init__(self, config_path, accounts_path="./accounts/"):
        self.conf = Config(config_path)
        self.accounts_path = accounts_path
        self.accounts = {}

    def confirmation(self, label, default="yes"):
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
                self.accounts["0x" + keyfile_json['address']] = \
                    eth_keyfile.decode_keyfile_json(keyfile_json, password.encode())
            except ValueError:
                raise ValueError("Incorrect password.")

    def load_web3(self, blockchain):
        return Web3(Web3.HTTPProvider(self.conf.blockchains[blockchain]['web3_uri']))

    def get_gas_oracle(self, blockchain):
        url_api = self.conf.blockchains[blockchain]['explorer-api']
        api_key = os.environ[self.conf.blockchains[blockchain]['api-token']]
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

    def extract_transactions_from_address(self, address, blockchain):
        for current_blockchain in blockchain:
            url_api = self.conf.blockchains[current_blockchain]['explorer-api']
            api_key = os.environ[self.conf.blockchains[current_blockchain]['api-token']]
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

            transactions = {}
            for transaction in response["result"]:
                if transaction["from"].lower() == address.lower():
                    transactions[transaction["hash"]] = transaction

            playbook_file = open("playbooks/playbook_" + current_blockchain + "_" + address[2:8] + ".yaml", "w")
            playbook_file.write(yaml.dump(transactions))
            playbook_file.close()

    def replicate_transaction(self, transaction_hash, account):
        # TODO
        pass

    def farm(self, password, playbook, param, keys_dir):
        self.load_accounts(password)

    def dispatch_currency(self, amount, from_address, blockchain, password):
        web3 = self.load_web3(blockchain)
        self.load_accounts(password)

        from_address = web3.toChecksumAddress(from_address)

        if from_address.lower() not in self.accounts:
            raise ValueError(from_address + " is not in " + self.accounts_path + ".")

        nb_dest_addresses = len(self.accounts) - 1

        self.confirmation(str(nb_dest_addresses * amount) + " " + self.conf.blockchains[blockchain]['symbol'] +
                          " will be sent to " + str(nb_dest_addresses) + " addresse(s). Confirm ?", 'no')

        if web3.eth.get_balance(from_address) <= amount:
            raise ValueError('Address ' + from_address + ' has only ' + self.conf.blockchains[blockchain]['symbol']
                             + ' and the operation needs at least ' + amount + ' '
                             + self.conf.blockchains[blockchain]['symbol'])

        gas_oracle = self.get_gas_oracle(blockchain)
        #TODO send transactions
