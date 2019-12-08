
import os
import json
import copy
import datetime
from functools import reduce

from . import NAME
from . import VERSION

from . import TelegramInterfaceCLIException
from . import TelegramInterfaceCLILogger
from . import TelegramInterfaceCLIConfig

from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerEmpty
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.errors.rpcerrorlist import ChatAdminRequiredError


class TelegramInterfaceCLI:

    debug = None
    output_format = None
    output_filename = None
    telegram_client = None

    telegram_api_id = None
    telegram_api_hash = None
    telegram_api_phone =None

    __chat_objects_by_id_hack = {}

    def __init__(self, config_filename, output_filename=None, output_format='json', debug=False):

        if debug:
            loglevel_env_override = '{}_LOGLEVEL'.format(NAME.replace('_', '').replace(' ', '').upper())
            os.environ[loglevel_env_override] = 'debug'

        global logger
        logger = TelegramInterfaceCLILogger().logger
        logger.info(NAME)
        logger.info('version {}'.format(VERSION))

        global config
        try:
            tgi_config = TelegramInterfaceCLIConfig(config_filename)
            config = tgi_config.config
            logger.debug('config_filename: {}'.format(tgi_config.config_filename))
        except TelegramInterfaceCLIException as e:
            logger.warn(e)
            config = {}

        self.telegram_api_id = os.environ.get('telegram_api_id', None)
        if self.telegram_api_id is None:
            if 'telegram_api_id' in config:
                self.telegram_api_id = config['telegram_api_id']
            else:
                logger.warn('Unable to set "telegram_api_id" value from env or config!')

        self.telegram_api_hash = os.environ.get('telegram_api_hash', None)
        if self.telegram_api_hash is None:
            if 'telegram_api_hash' in config:
                self.telegram_api_hash = config['telegram_api_hash']
            else:
                logger.warn('Unable to set "telegram_api_hash" value from env or config!')

        self.telegram_api_phone = os.environ.get('telegram_api_phone', None)
        if self.telegram_api_phone is None:
            if 'telegram_api_phone' in config:
                self.telegram_api_phone = config['telegram_api_phone']
            else:
                logger.warn('Unable to set "telegram_api_phone" value from env or config!')

        self.output_format = output_format
        self.output_filename = output_filename

        logger.debug('output_format: {}'.format(self.output_format))
        logger.debug('output_filename: {}'.format(self.output_filename))
        logger.debug('telegram_api_id: {}'.format(self.telegram_api_id))
        logger.debug('telegram_api_hash: {}'.format(self.telegram_api_hash))
        logger.debug('telegram_api_phone: {}'.format(self.telegram_api_phone))

    def main(self, data_filename=None, groups=False, users=False):

        if data_filename is None:
            ts = str(datetime.datetime.utcnow()).split('.')[0].replace(' ', 'Z').replace('-', '').replace(':', '')
            data_filename = '{}-{}.json'.format(self.telegram_api_phone, ts)

        if os.path.isfile(data_filename):
            logger.info('Loading data file: {}'.format(data_filename))
            with open(data_filename, 'r') as f:
                telegram_data = json.load(f)
        else:
            logger.info('Saving to data file: {}'.format(data_filename))

            session_filename = None
            if 'session_filename' in config:
                session_filename = config['session_filename']

            try:
                connect_telegram = self.connect_telegram(session_filename=session_filename)
            except ValueError as e:
                logger.error(e)
                return

            if connect_telegram is False:
                logger.error('Failed connecting to Telegram')
                return

            telegram_data = {'chat_groups': self.get_chat_groups(expansions=['users'])}

            with open(data_filename, 'w') as f:
                json.dump(telegram_data, f)

        if users is True and groups is False:
            output_data = self.extract_users(telegram_data)
        elif users is False and groups is True:
            output_data = self.extract_groups(telegram_data)
        else:
            output_data = self.extract_groups(telegram_data, users_expansion=True)
        self.output(output_data)
        return

    def output(self, data):
        if self.output_format.lower() == 'csv':
            out = self.flatten_to_csv(data)
        else:
            out = json.dumps(data, indent=2)

        if self.output_filename == '-' or self.output_filename is None:
            print(out)
        else:
            with open(self.output_filename, 'w') as f:
                f.write(out)
            logger.info('Output written to filename: {}'.format(self.output_filename))

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
                            'phone': user['phone'],
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

    def connect_telegram(self, session_filename=None):

        if session_filename is None:
            session_filename = '__CWD__/{}.session'.format(self.telegram_api_phone).replace('__CWD__', os.getcwd())
        else:
            session_filename = os.path.expanduser(session_filename)
        logger.info('Session filename: {}'.format(session_filename))

        self.telegram_client = TelegramClient(session_filename, self.telegram_api_id, self.telegram_api_hash)
        self.telegram_client.connect()

        if not self.telegram_client.is_user_authorized():
            self.telegram_client.send_code_request(self.telegram_api_phone)
            self.telegram_client.sign_in(
                self.telegram_api_phone,
                input('Enter the MFA code provided to you in the Telegram application: ')
            )
        logger.info('Connected to Telegram with telegram_api_id: {}'.format(self.telegram_api_id))
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
        try:
            channel_users = self.telegram_client.get_participants(chat_channel_object)
            return self.cast_jsonable(channel_users)
        except ChatAdminRequiredError as e:
            logger.warn('Failed get users from {}, admin privilege required'.format(chat_channel_object.title))
            return list()


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
            raise TelegramInterfaceCLIException('Unsupported object type encountered while attempting to __flatten_object()')
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
