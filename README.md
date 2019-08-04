# Telegram Interface

A quick tool for listing out the Telegram Messenger groups your user-account is invited into and
the users within each.

### Github
* [github.com/ndejong/telegram-interface](https://github.com/ndejong/telegram-interface)

### Prerequisites
* A [Telegram Messenger](https://telegram.org/) account invited into one or more group chat channels.
* Setup API credentials on the Telegram Messenger account [core.telegram.org/api/obtaining_api_id](https://core.telegram.org/api/obtaining_api_id)

### Environment Variables
The following environment variables must be set with their associated values:-
* `telegram_api_id`
* `telegram_api_hash`
* `telegram_api_phone`

### Outputs
All output is JSON data-structures making it easier to chain with other tools such as `jq` for further parsing and 
filtering if required.

Log status messages are sent to stdout thus do not get in the way of tool chaining.

#### Example: trivial output filtering using `jq`
```commandline
telegram-interface.py -f +000000000000-20190804Z072817.json -g | jq .[].name 
20190804Z085638 - Telegram Interface
20190804Z085638 - Loading data file: +000000000000-20190804Z072817.json
"Awesome Group A"
"Another Group"
"A Chat Forum"
```

#### Example: extracting from the saved data-file using `jq`
```commandline
cat +000000000000-20190804Z072817.json | jq '.chat_groups[].megagroup, .chat_groups[].title'
true
true
null
"Awesome Group A"
"Another Group"
"A Chat Forum"
```

### Usage
```
usage: telegram-interface.py [-h] [-e] [-f <filename>] [-o <filename>] [-g]
                             [-u]

Telegram Interface

optional arguments:
  -h, --help     show this help message and exit
  -e             Output the current environment variable values and exit.
  -f <filename>  Data filename to use, if the file already exists it will be
                 loaded as input without connecting to Telegram. By default
                 auto-generates a filename in the <cwd>.
  -o <filename>  Output filename, by default to <stdout>
  -g             Output groups, can be used with -u to obtain users in groups
  -u             Output users
```

****

## Authors
[Nicholas de Jong](https://nicholasdejong.com)

## License
BSD-2-Clause - see LICENSE file for full details.
