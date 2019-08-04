# Telegram Interface

A quick tool for listing the Telegram Messenger groups that a user-account is invited into and
listing the users within groups.

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

Log status messages are sent to stderr and do not get in the way of pipe style tool chaining.

#### Example: trivial output filtering using `jq`
```commandline
telegram-interface.py -g | jq .[].name 
20190804Z085638 - Telegram Interface
20190804Z085638 - Saving to data file: +000000000000-20190804Z072817.json
20190804Z085638 - Connected to Telegram with api_id: 12345
"Awesome Group A"
"Another Group"
"A Chat Forum"
...
```

#### Example: extract list of users as a csv using `jq`
```commandline
telegram-interface.py -f +000000000000-20190804Z072817.json -u | jq -r '(.[0] | keys_unsorted) as $keys | $keys, map([.[ $keys[] ]])[] | @csv'
20190804Z145459 - Telegram Interface
20190804Z145459 - Loading data file: +000000000000-20190804Z072817.json
"id","username","firstname","lastname"
123456789,"awesomeuser","Awesome","User"
234567878,"someotheruser","Some","Other User"
236423423,"givemeuser","Give","Me"
...
```

#### Example: extracting the megagroup field directly from saved data using `jq` and a `tr` hack
```commandline
cat +000000000000-20190804Z072817.json | jq '.chat_groups[]| "\(.id)~,~\(.title)~,~\(.megagroup)"' | tr '~' '"'
"183982374","Awesome Group A","true"
"198123123","Another Group","null"
"1734975345","A Chat Forum","true"
...
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
