import yaml


class Config:

    def __init__(self, config_path):
        with open(config_path, "r") as stream:
            try:
                parsed_conf = yaml.safe_load(stream)
                self.blockchains = parsed_conf['blockchains']
            except yaml.YAMLError as exc:
                print(exc)
