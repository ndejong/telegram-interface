#!/usr/bin/env python3

import os
import sys
import json
import copy
import datetime
import argparse
from functools import reduce

from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerEmpty
from telethon.tl.functions.messages import GetDialogsRequest


class TelegramInterfaceException(Exception):
    pass


class TelegramInterface:

    args = None
    name = 'Telegram Interface'
    telegram_client = None
    __chat_objects_by_id_hack = {}

    def __init__(self):
        parser = argparse.ArgumentParser(description=self.name)

        parser.add_argument('-e', '--env', action='store_true', default=False,
                            help='Output the current environment variable values and exit.')

        parser.add_argument('-f', type=str, metavar='<filename>', default=None,
                            help='Data filename to use, if the file already exists it will be loaded as input without '
                                 'connecting to Telegram.  By default auto-generates a filename in the <cwd>.')

        parser.add_argument('-o', type=str, metavar='<filename>', default='-',
                            help='Output filename, by default to <stdout>')

        parser.add_argument('-c', '--csv', action='store_true', default=False,
                            help='Output in flattened CSV format')

        parser.add_argument('-g', action='store_true', default=False,
                            help='Output groups, can be used with -u to obtain users in groups')

        parser.add_argument('-u', action='store_true', default=False,
                            help='Output users')

        self.args = parser.parse_args()
        if self.args.env is False and self.args.g is False and self.args.u is False:
            parser.print_help()
            exit(1)

    def main(self):
        self.message_stderr(self.name, color='grey')

        if self.args.env is True:
            self.output(self.get_environment_variables())
            return

        telegram_data_filename = self.args.f
        if telegram_data_filename is None:
            api_phone = self.get_environment_variables()['telegram_api_phone']
            if not api_phone:
                self.message_stderr('Environment variable "telegram_api_phone" not set!', color='red')
                return
            telegram_data_filename = '{}-{}.json'.format(api_phone, self.timestamp())

        telegram_data = None
        if os.path.isfile(telegram_data_filename):
            self.message_stderr('Loading data file: {}'.format(telegram_data_filename), color='grey')
            with open(telegram_data_filename, 'r') as f:
                telegram_data = json.load(f)
        else:
            self.message_stderr('Saving to data file: {}'.format(telegram_data_filename), color='grey')
            if self.connect_telegram() is False:
                self.message_stderr('Failed connecting to Telegram', color='red')
                return
            telegram_data = {
                'chat_groups': self.get_chat_groups(expansions=['users'])
            }
            with open(telegram_data_filename, 'w') as f:
                json.dump(telegram_data, f)

        output_data = None
        if self.args.u is True and self.args.g is False:
            output_data = self.extract_users(telegram_data)
        elif self.args.u is False and self.args.g is True:
            output_data = self.extract_groups(telegram_data)
        else:
            output_data = self.extract_groups(telegram_data, users_expansion=True)

        self.output(output_data)
        return

    def timestamp(self):
        return str(datetime.datetime.utcnow()).split('.')[0].replace(' ', 'Z').replace('-', '').replace(':', '')

    def get_environment_variables(self):
        return {
            'telegram_api_id': os.environ.get('telegram_api_id', None),
            'telegram_api_hash': os.environ.get('telegram_api_hash', None),
            'telegram_api_phone': os.environ.get('telegram_api_phone', None),
        }

    def output(self, data):
        if self.args.csv is True:
            out = self.flatten_to_csv(data)
        else:
            out = json.dumps(data, indent=2)

        if self.args.o == '-':
            print(out)
        else:
            with open(self.args.o, 'w') as f:
                f.write(out)
            self.message_stderr('Output written to filename: {}'.format(self.args.o), color='grey')

    def message_stderr(self, message, timestamp=True, color='default', end='\n'):

        if color.lower() == 'red':
            color_code = '\x1b[31m'
        elif color.lower() == 'blue':
            color_code = '\x1b[34m'
        elif color.lower() == 'green':
            color_code = '\x1b[32m'
        elif color.lower() == 'yellow':
            color_code = '\x1b[33m'
        elif color.lower() in ['grey', 'gray']:
            color_code = '\x1b[90m'
        elif color.lower() == 'white':
            color_code = '\x1b[97m'
        else:
            color_code = '\x1b[39m'

        if timestamp:
            message = '{} - {}'.format(self.timestamp(), message.strip())

        color_default = '\x1b[0m'

        sys.stderr.write(color_code + message + color_default + end)
        return

    def extract_users(self, telegram_data):
        users_list = []
        users_id_list = []
        for group in self.extract_groups(telegram_data, users_expansion=True):
            for user in group['users']:
                if user['id'] not in users_id_list:
                    users_id_list.append(user['id'])
                    users_list.append(user)
        return users_list

    def extract_groups(self, telegram_data, users_expansion=False):
        groups_list = []
        groups_id_list = []
        for chat_group in telegram_data['chat_groups']:
            if chat_group['id'] not in groups_id_list:
                groups_id_list.append(chat_group['id'])
                users_list = []
                if users_expansion is True:
                    for user in chat_group['users']:
                        users_list.append({
                            'id': user['id'],
                            'username': user['username'],
                            'firstname': user['first_name'],
                            'lastname': user['last_name'],
                        })
                    groups_list.append({
                        'id': chat_group['id'],
                        'name': chat_group['title'],
                        'users': users_list
                    })
                else:
                    groups_list.append({
                        'id': chat_group['id'],
                        'name': chat_group['title']
                    })
        return groups_list

    def connect_telegram(self):
        env = self.get_environment_variables()

        if env['telegram_api_id']:
            api_id = env['telegram_api_id']
        else:
            self.message_stderr('Environment variable "telegram_api_id" not set!', color='red')
            return False

        if env['telegram_api_hash']:
            api_hash = env['telegram_api_hash']
        else:
            self.message_stderr('Environment variable "telegram_api_hash" not set!', color='red')
            return False

        if env['telegram_api_phone']:
            api_phone = env['telegram_api_phone']
        else:
            self.message_stderr('Environment variable "telegram_api_phone" not set!', color='red')
            return False

        self.telegram_client = TelegramClient(api_phone, api_id, api_hash)

        self.telegram_client.connect()
        if not self.telegram_client.is_user_authorized():
            self.telegram_client.send_code_request(os.environ.get('telegram_api_phone'))
            self.telegram_client.sign_in(
                os.environ.get('telegram_api_phone'),
                input('Enter the MFA code provided to you in the Telegram application: ')
            )
        self.message_stderr('Connected to Telegram with api_id: {}'.format(api_id), color='grey')
        return True

    def get_chat_groups(self, expansions=None, limit=9999):
        if expansions is None:
            expansions = []

        chat_channels = self.get_chats_by_attribute(attribute='participants_count', limit=limit)

        if 'users' in expansions:
            for channel_index, channel in enumerate(chat_channels):
                channel_id = str(channel['id'])
                chat_channels[channel_index]['users'] = self.get_chat_users(self.__chat_objects_by_id_hack[channel_id])

        return chat_channels

    def get_chat_users(self, chat_channel_object):
        channel_users = self.telegram_client.get_participants(chat_channel_object)
        return self.cast_jsonable(channel_users)

    def get_chats_by_attribute(self, attribute, limit=10):
        chats = []
        result = self.telegram_client(
            GetDialogsRequest(
                offset_date=None,
                offset_id=0,
                offset_peer=InputPeerEmpty(),
                limit=limit,
                hash=0
            )
        )

        result_count = 0
        if hasattr(result, 'chats'):
            result_count = len(result.chats)

        if result_count > 0:
            for chat in result.chats:
                if hasattr(chat, attribute):
                    self.__chat_objects_by_id_hack[str(chat.id)] = chat
                    chats.append(self.cast_jsonable(chat))
        return chats

    def cast_jsonable(self, obj, __depth=0, __depth_limit=8):

        if __depth >= __depth_limit:
            return '<< OBJECT DEPTH LIMIT >>'

        if obj is None or type(obj) in [int, float, str, bool]:
            return obj

        if type(obj) is list or 'List' in type(obj).__name__:
            result = []
            for item in obj:
                result.append(self.cast_jsonable(item, __depth+1))
            return result

        if not hasattr(obj, '__dict__'):
            return obj.__str__()

        result = {}
        for attribute in obj.__dict__:
            result[attribute] = self.cast_jsonable(obj.__dict__[attribute], __depth+1)
        return result

    def flatten_to_csv(self, obj, delimiter='.'):
        flat_obj = self.__flatten_object(obj, delimiter=delimiter)

        data = []
        data_row = {}
        data_row_keys = []
        data_row_last = None
        line_number_previous = -1
        for flat_key in flat_obj:
            key = self.__flattened_key_parse(flat_key, method='key', delimiter=delimiter)
            line_number = self.__flattened_key_parse(flat_key, method='line', delimiter=delimiter)
            if line_number != line_number_previous:
                if data_row:
                    data.append(copy.copy(data_row))
                line_number_previous = line_number
            data_row[key] = flat_obj[flat_key]
            if key not in data_row_keys:
                data_row_keys.append(key)
            data_row_last = data_row
        data.append(copy.copy(data_row_last))

        # return json.dumps(data, indent=2)

        def __csv_row(list_items, char='"', end='\n'):
            return char + '{char},{char}'.format(char=char).join(str(x) for x in list_items) + char + end

        csv = __csv_row(data_row_keys)
        for row in data:
            row_list = []
            for data_row_key in data_row_keys:
                if data_row_key in row:
                    row_list.append(row[data_row_key])
                else:
                    row_list.append('')
            csv += __csv_row(row_list)
        return csv.rstrip('\n')

    def __flatten_object(self, obj, parent_key='', delimiter='.'):
        items = []
        if type(obj) is list:
            for list_index, value in enumerate(obj):
                new_key = '{}{}{}'.format(parent_key, delimiter, str(list_index)) if parent_key else str(list_index)
                if type(value) in (str, int, float, bool):
                    items.append((new_key, value))
                else:
                    items.extend(self.__flatten_object(value, new_key, delimiter=delimiter).items())
        elif type(obj) is dict:
            for key, value in obj.items():
                new_key = '{}{}{}'.format(parent_key, delimiter, key) if parent_key else key
                if type(value) in (str, int, float, bool) or value is None:
                    items.append((new_key, value))
                else:
                    items.extend(self.__flatten_object(value, new_key, delimiter=delimiter).items())
        else:
            raise TelegramInterfaceException('Unsupported object type encountered while attempting to __flatten_object()')
        return dict(items)

    def __flattened_key_parse(self, flat_key, method='key', delimiter='.'):
        if method.lower() == 'key':
            key = ''
            for flat_key_part in flat_key.split(delimiter):
                if not flat_key_part.isdigit():
                    key = '{}{}{}'.format(key, delimiter, flat_key_part) if key else flat_key_part
            return key
        else:
            flat_key_part_numbers = []
            for flat_key_part in flat_key.split(delimiter):
                if flat_key_part.isdigit():
                    flat_key_part_numbers.append(int(flat_key_part) + 1)
            return reduce((lambda x, y: x * y), flat_key_part_numbers)


TelegramInterface().main()
