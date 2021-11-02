import os
import yaml





from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/6eacb828d63246bb85f6104f0312c402'))


def load(self):
    # Increment the y-position of the rocket.
    self.y += 1

# address_dir = "accounts/Account 1/"
# address_from = os.listdir("accounts/Account 1/")[0]
# file = open(address_dir + address_from, "r")
# private_key = file.read()
# file.close()
#
# print(private_key)
#
# address = Web3.toChecksumAddress(address_from)
# print(w3.eth.get_block('latest'))
