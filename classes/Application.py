import os
import eth_keyfile

from classes.Config import Config


class Application:

    def __init__(self, config_path):
        self.conf = Config(config_path)

    def create_accounts(self, number, path, password):
        # TODO
        # eth_keyfile.create_keyfile_json(self.conf.accounts_folder)
        pass

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
