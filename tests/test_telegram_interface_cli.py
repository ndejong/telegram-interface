
import os
import tempfile
import pytest
from unittest.mock import patch
import telegram_interface_cli


def test_version_exist():
    assert telegram_interface_cli.__version__ is not None


def test_name_exist():
    assert telegram_interface_cli.__name__ is not None


def test_telegram_interface_cli_init():
    config_filename = __faux_config_file()
    os.environ['TELEGRAMINTERFACECLI_CONFIG_FILENAME'] = config_filename
    x = telegram_interface_cli.TelegramInterfaceCLI(debug=True)
    os.unlink(config_filename)
    assert x is not None


# TODO: add more tests with deeper coverage


def __faux_config_file(filename=None):
    if filename is None:
        filename = tempfile.mktemp()

    faux_config = """
telegram_interface_cli:
  telegram_api_id: XX
  telegram_api_hash: XX
  telegram_api_phone: XX
  session_filename: '/tmp/test_telegram_interface_cli.session'
"""

    with open(filename, 'w') as f:
        f.write(faux_config)
    return filename
