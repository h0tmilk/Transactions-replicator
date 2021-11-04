import argparse
from getpass import getpass

from classes.Application import Application

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest='function')

    # Create accounts parser
    parser_create_accounts = subparsers.add_parser('create_accounts')
    parser_create_accounts.add_argument('-n', '--number', type=int, help='Number of accounts to create.', required=True)
    parser_create_accounts.add_argument('-p', '--password', help='Password for keyfiles.')
    parser_create_accounts.add_argument('-d', '--directory', help='Directory where keyfiles will be generated.',
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

    # Instantiate Application
    application = Application("./config/config.yaml")

    args = parser.parse_args()
    if args.function == 'create_accounts':
        if not args.password:
            try:
                password = getpass(prompt='Enter a password for keyfiles: ')
                application.create_accounts(args.number, args.directory, password)
            except Exception as error:
                print('ERROR', error)
        else:
            application.create_accounts(args.number, args.directory, args.password)

    elif args.subcommand == 'extract_transactions':
        application.extract_transactions_from_address(args.address, args.blockchains.split(','))

    elif args.subcommand == 'farm':
        application.farm(args.password, args.playbook, args.blockchains.split(','), args.keys_dir)
