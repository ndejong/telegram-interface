
import os
import yaml

from . import __name__
from . import TelegramInterfaceCLIException


class TelegramInterfaceCLIConfig:

    debug = False
    config = None
    config_root = __name__
    config_filename = None

    def __init__(self, config_filename_env_override=None):

        if config_filename_env_override is None:
            config_filename_env_override = '{}_CONFIG_FILENAME'.format(__name__.replace('_', '').replace(' ', '').upper())

        if os.getenv(config_filename_env_override) is not None:
            self.config_filename = os.path.expanduser(os.getenv(config_filename_env_override))

        if self.config_filename is None:
            self.config_filename = self.__find_config()

        if self.config_filename is None or not os.path.isfile(self.config_filename):
            raise TelegramInterfaceCLIException('Unable to locate configuration file',self.config_filename)

        self.config = self.__load_config(self.config_filename)

    def __find_config(self):
        candidate_paths = [
            '__CWD__/telegram_interface_cli.yml',
            '__CWD__/telegram_interface_cli.yaml',
            '__CWD__/telegram-interface.yml',
            '__CWD__/telegram-interface.yaml',
            '~/.telegram-interface',
            '/etc/telegram-interface/telegram-interface.yml',
            '/etc/telegram-interface/telegram-interface.yaml',
        ]
        for candidate_path in candidate_paths:
            path = os.path.expanduser(candidate_path.replace('__CWD__', os.getcwd()))
            if os.path.exists(path):
                return path
        return None

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
