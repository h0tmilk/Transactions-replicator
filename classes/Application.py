import json
import os
import eth_keyfile
import secrets
from sha3 import keccak_256

from classes.Config import Config


class Application:

    def __init__(self, config_path):
        self.conf = Config(config_path)

    def create_accounts(self, number, path, password):
        for x in range(number):
            private_key = keccak_256(secrets.token_bytes(32)).digest()
            keyfile_content = eth_keyfile.create_keyfile_json(private_key, password.encode())
            address = keyfile_content["address"]

            keyfile = open(path + "/keyfile_" + address[:5], "w")
            keyfile.write(json.dumps(keyfile_content, indent=4))
            keyfile.close()

    def load_accounts(self, path):
        for x in os.walk(self.conf.accounts_folder):
            print(x[0])
        # address_dir = "accounts/Account 1/"
        # address_from = os.listdir("accounts/Account 1/")[0]
        # file = open(address_dir + address_from, "r")
        # private_key = file.read()
        # file.close()
        # TODO
        pass

    def extract_transactions_from_address(self, address, blockchain):
        # TODO
        pass

    def send_transaction(self, raw_transaction, account):
        # TODO
        pass

    def replicate_transaction(self, transaction_hash, account):
        # TODO
        pass

    def farm(self, password, playbook, param, keys_dir):
        # TODO
        pass
