from secrets import token_bytes
from coincurve import PublicKey
from sha3 import keccak_256
import os

ACCOUNTS_FOLDER = './accounts/'

private_key = keccak_256(token_bytes(32)).digest()
public_key = PublicKey.from_valid_secret(private_key).format(compressed=False)[1:]
addr = keccak_256(public_key).digest()[-20:]

# Count the number of existing accounts
noOfDir = 0
for base, dirs, files in os.walk(ACCOUNTS_FOLDER):
    for directories in dirs:
        noOfDir += 1
accounts_number = noOfDir
# Create the folder
account_dirname = ACCOUNTS_FOLDER + "Account " + str(accounts_number+1)
os.mkdir(account_dirname)
# Create file (filename = address, content = key)
file = open(account_dirname + "/0x" + addr.hex(), "w")
file.write(private_key.hex())
file.close()