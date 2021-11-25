import argparse
from getpass import getpass

from classes.Application import Application

if __name__ == "__main__":
    CONFIG_PATH = "./config/config.yaml"

    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest='function')

    # Create accounts parser
    parser_create_accounts = subparsers.add_parser('create_accounts')
    parser_create_accounts.add_argument('-n', '--number', type=int, help='Number of accounts to create.', required=True)
    parser_create_accounts.add_argument('-p', '--password', help='Password for keyfiles.')
    parser_create_accounts.add_argument('-d', '--directory', help='Directory where keyfiles will be generated.',
                                        default='./accounts/')

    # Dispatch currency parser
    parser_dispatch_currency = subparsers.add_parser('dispatch_currency')
    parser_dispatch_currency.add_argument('-a', '--amount', type=float, help='Amount of tokens to send to each address.', required=True)
    parser_dispatch_currency.add_argument('-f', '--from_address', help='Address which will send tokens.', required=True)
    parser_dispatch_currency.add_argument('-b', '--blockchain',
                                             help='Blockchain name where transactions will be made '
                                                  '(see config file).',
                                             required=True)
    parser_dispatch_currency.add_argument('-p', '--password', help='Password of sender address keyfile.', required=True)
    parser_dispatch_currency.add_argument('-k', '--keys_dir', help='Directory where keyfiles are located.',
                                        default='./accounts/')

    # Extract transactions parser
    parser_extract_transactions = subparsers.add_parser('extract_transactions')
    parser_extract_transactions.add_argument('-a', '--address',
                                             help='Address from which transaction have to be extracted.',
                                             required=True)
    parser_extract_transactions.add_argument('-b', '--blockchains',
                                             help='Blockchains names from which transactions have to be extracted '
                                                  '(see config file), separated by commas.',
                                             required=True)

    # Farm parser
    farm = subparsers.add_parser('farm')
    farm.add_argument('-p', '--password', help='Password of keyfiles.', required=True)
    farm.add_argument('-b', '--blockchains',
                                             help='Blockchain names from which transactions have to be extracted '
                                                  '(see config file), separated by commas.',
                                             required=True)
    farm.add_argument('-P', '--playbook', help='Playbook file containing transactions and blockchains (generated with '
                                               'extract_transactions function.', required=True)
    farm.add_argument('-k', '--keys_dir', help='Directory where keyfiles are located.',
                                        default='./accounts/')

    args = parser.parse_args()
    if args.function == 'create_accounts':
        application = Application(CONFIG_PATH, args.directory)
        if not args.password:
            try:
                password = getpass(prompt='Enter a password for keyfiles: ')
                application.create_accounts(args.number, args.directory, password)
            except Exception as error:
                print('ERROR', error)
        else:
            application.create_accounts(args.number, args.directory, args.password)

    elif args.function == 'extract_transactions':
        application = Application(CONFIG_PATH)
        application.extract_transactions_from_address(args.address, args.blockchains.split(','))

    elif args.function == 'dispatch_currency':
        application = Application(CONFIG_PATH, args.keys_dir)
        application.dispatch_currency(args.amount, args.from_address, args.blockchain, args.password)

    elif args.function == 'farm':
        application = Application(CONFIG_PATH, args.keys_dir)
        application.farm(args.password, args.playbook, args.blockchains.split(','))
