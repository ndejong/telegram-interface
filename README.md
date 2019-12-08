# Telegram Interface

[![PyPi](https://img.shields.io/pypi/v/telegram-interface-cli.svg)](https://pypi.org/project/telegram-interface-cli/)
[![Build Status](https://api.travis-ci.org/ndejong/telegram-interface.svg?branch=master)](https://travis-ci.org/ndejong/telegram-interface)

A quick tool for listing the Telegram Messenger groups that a user-account is invited into and
listing the users within groups.

## Project
* [github.com/ndejong/telegram-interface](https://github.com/ndejong/telegram-interface)

## Install
#### via PyPi
```bash
pip3 install telegram-interface-cli
```

#### via Source
```bash
git clone https://github.com:ndejong/telegram-interface
cd telegram-interface
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 setup.py clean
python3 setup.py test
python3 setup.py install
```

## Prerequisites
* A [Telegram Messenger](https://telegram.org/) account invited into one or more group chat channels.
* Setup API credentials on the Telegram Messenger account [core.telegram.org/api/obtaining_api_id](https://core.telegram.org/api/obtaining_api_id)

## Configuration

Configuration is via a YAML format as per the following example
```yaml

---

telegram_interface_cli:

#
#  api_id: env:telegram_api_id
#  api_hash: env:telegram_api_hash
#  api_phone: env:telegram_api_phone
#

  api_id: '123456'
  api_hash: '0123456789abcdef0123456789abcdef'
  api_phone: '12125551234'

  session_filename: '~/.telegram.session'

```

Loading environment variables into the configuration file is possible using the env name with an 
`env:` prefix, for example
```yaml
  api_id: env:telegram_api_id
``` 
In this case the `api_id` value is loaded loaded from the `telegram_api_id` env value.

#### Environment Variables
* `TELEGRAMINTERFACECLI_CONFIG_FILENAME` - configuration file override.

## Outputs
By default output is in JSON data-structures making it easier to chain with other tools such as `jq` for further parsing 
and filtering if required.

Additionally, CSV outputs are possible using the `--csv` argument. 

Log status messages are sent to stderr and do not get in the way of pipe style tool chaining.



### Usage
```
usage: telegram-interface [-h] [-c <filename>] [-f <filename>] [-o <filename>]
                          [-g] [-u] [--csv] [-d]

Telegram Interface v0.1.4

optional arguments:
  -h, --help     show this help message and exit
  -c <filename>  Configuration file to use (required)
  -f <filename>  Data filename to use. If the data-file already exists it will
                 be loaded as input without connecting to Telegram thus
                 allowing a reload of a previous run. By default a filename is
                 auto-generated in the current-working-directory.
  -o <filename>  Output filename, by default output is sent to <stdout>.
  -g, --group    Output names of groups that the Telegram user is a member of,
                 combine with -u to obtain the users within these groups.
  -u, --user     Output names of the users that the Telegram user has
                 visibility on.
  --csv          Output in flattened CSV format.
  -d, --debug    Debug level logging output.

A quick tool for listing the Telegram Messenger groups that a user-account is
invited into and listing the users within groups.
```

****

## Authors
[Nicholas de Jong](https://nicholasdejong.com)

## License
BSD-2-Clause - see LICENSE file for full details.
