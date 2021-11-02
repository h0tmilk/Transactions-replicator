from classes.Config import Config


class Application:

    def __init__(self, config_path):
        self.conf = Config(config_path)

    def extract_transactions_from_address(self, address):
        #TODO

    def send_transaction(self, raw_transaction, account):
        # TODO

    def replicate_transaction(self, transaction_hash, account):
        #TODO
