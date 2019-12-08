
import os
import yaml

from . import NAME
from . import TelegramInterfaceCLIException


class TelegramInterfaceCLIConfig:

    debug = False
    config = None
    config_root = NAME
    config_filename = None

    def __init__(self, config_filename=None):

        if config_filename is None:
            config_filename = os.getenv('TELEGRAMINTERFACECLI_CONFIG_FILENAME')

        if config_filename is not None:
            config_filename = os.path.expanduser(config_filename)

        if config_filename is None or not os.path.isfile(config_filename):
            raise TelegramInterfaceCLIException('Unable to locate configuration file: {}'.format(config_filename))

        self.config = self.__load_config(config_filename)
        self.config_filename = config_filename

    def __load_config(self, config_filename):
        loaded_config = {}

        with open(config_filename, 'r') as f:
            try:
                loaded_config = yaml.safe_load(f.read().replace('@timestamp', '__timestamp'))
            except yaml.YAMLError as e:
                raise TelegramInterfaceCLIException(e)

        def replace_env_values(input):
            if input is None:
                return input
            elif type(input) in (int, bool):
                return input
            elif type(input) is str:
                if input.lower()[0:4] == 'env:':
                    env_name = input.replace('env:', '')
                    self.__debug('Config element set via env value {}'.format(env_name))
                    value = os.getenv(env_name, None)
                    if value is None or len(value) < 1:
                        raise TelegramInterfaceCLIException('Config requested env value not set', env_name)
                    return value
                return input
            elif type(input) is list:
                r = []
                for item in input:
                    r.append(replace_env_values(item))
                return r
            elif type(input) is dict:
                r = {}
                for item_k, item_v in input.items():
                    r[item_k] = replace_env_values(item_v)
                return r
            else:
                raise TelegramInterfaceCLIException('Unsupported type in replace_env_values()', input)

        loaded_config = replace_env_values(loaded_config)

        if type(loaded_config) is not dict or self.config_root not in loaded_config.keys():
            raise TelegramInterfaceCLIException('Unable to locate config root', self.config_root)

        return loaded_config[self.config_root]

    def __debug(self, message):
        if self.debug:
            print('TelegramInterfaceCLIException debug: {}'.format(message))
