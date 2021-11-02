import yaml


class Config:

    def __init__(self, config_path):
        with open(config_path, "r") as stream:
            try:
                self.accounts_folder = yaml.safe_load(stream)['airdrop_autofarmer'][0]['accounts_folder']
                #TODO add blockchain loading
            except yaml.YAMLError as exc:
                print(exc)
