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
By default output is in JSON data-structures making it easier to chain with other tools such as `jq` for further parsing 
and filtering if required.

Additionally, CSV outputs are possible using the `--csv` argument. 

Log status messages are sent to stderr and do not get in the way of pipe style tool chaining.

#### Example: List groups names using `jq` to filter output
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

#### Example: List groups names using `--csv` argument. 
```commandline
telegram-interface.py -g -c
20190804Z085638 - Telegram Interface
20190804Z085638 - Saving to data file: +000000000000-20190804Z072817.json
20190804Z085638 - Connected to Telegram with api_id: 12345
"id","name"
"1115000000","Awesome Group A"
"1020000000","Another Group"
"110090000","A Chat Forum"
...
```


#### Example: List members of all groups using the `--csv` argument from previous datafile.
```commandline
telegram-interface.py -f +000000000000-20190804Z072817.json -u -g -c
20190804Z145459 - Telegram Interface
20190804Z145459 - Loading data file: +000000000000-20190804Z072817.json
"id","name","users.id","users.username","users.firstname","users.lastname"
"1115000000","Awesome Group A","977000000","user_one","User","One"
"1115000000","Awesome Group A","190000000","someotheruser","Some","Other User"
"1115000000","Awesome Group A","790000000","awesomeuser","Awesome","User"
...
```


### Usage
```
usage: telegram-interface.py [-h] [-e] [-f <filename>] [-o <filename>] [-c]
                             [-g] [-u]

Telegram Interface

optional arguments:
  -h, --help     show this help message and exit
  -e, --env      Output the current environment variable values and exit.
  -f <filename>  Data filename to use, if the file already exists it will be
                 loaded as input without connecting to Telegram. By default
                 auto-generates a filename in the <cwd>.
  -o <filename>  Output filename, by default to <stdout>
  -c, --csv      Output in flattened CSV format
  -g             Output groups, can be used with -u to obtain users in groups
  -u             Output users
```

****

## Authors
[Nicholas de Jong](https://nicholasdejong.com)

## License
BSD-2-Clause - see LICENSE file for full details.
