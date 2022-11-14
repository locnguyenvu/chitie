import sqlalchemy as sa
import telegram
import telegram.error

from abc import abstractmethod
from chitie.i18n import t
from chitie.util import timerange
from flask import current_app
from urllib.parse import parse_qs, urlencode
from typing import Union
from .chatcontext import Chatcontext


def get_chatcontext(message: 'Message') -> Union[None, Chatcontext]:
    tr = timerange.from_str('today')
    return Chatcontext.query.filter(sa.and_(
        Chatcontext.created_at >= tr.time_from,
        Chatcontext.created_at <= tr.time_to)).filter_by(
            is_active=True,
            chat_id=message.chat.id,
            user_id=message.from_user.id).first()


class Bot(telegram.Bot):

    def talks(self, text, parse_mode=None):
        chat_id = current_app.config['bot.group_id']
        if parse_mode is None:
            content = t(text)
            super().send_message(chat_id, content)
        if parse_mode == telegram.ParseMode.MARKDOWN_V2:
            super().send_message(chat_id, text, parse_mode=telegram.ParseMode.MARKDOWN_V2)


class Message(telegram.Message):

    def command(self) -> str:
        if self.entities is None or len(self.entities) == 0:
            return ''
        for entity in self.entities:
            if entity.type == telegram.MessageEntity.BOT_COMMAND:
                return self.text[entity.offset:entity.length + entity.offset].lstrip('/')
        return ''

    def is_command(self) -> bool:
        if self.entities is None or len(self.entities) == 0:
            return False
        for entity in self.entities:
            if entity.type == telegram.MessageEntity.BOT_COMMAND:
                return True
        return False

    def argumentstr(self):
        if not self.is_command():
            return None
        args = ''
        for entity in self.entities:
            if entity.type == telegram.MessageEntity.BOT_COMMAND:
                args = self.text[entity.offset + entity.length:]
                break
        return args.strip()


class CallbackQuery(telegram.CallbackQuery):

    def function(self) -> str:
        data_chunks = self.data.split('|')
        return data_chunks[0]

    def arguments(self) -> dict:
        data_chunks = self.data.split('|')
        rawdict = parse_qs(data_chunks[1])
        result = {}
        for key in rawdict.keys():
            value = rawdict[key]
            if len(value) == 1:
                result[key] = value[0]
                continue
            result[key] = value
        return result


class Handler:

    def __init__(self):
        self._next = None

    def set_next(self, handler: 'Handler'):
        self._next = handler
        return handler

    def process(self, event: 'Message') -> bool:
        if self.match(event):
            self.exec(event)
            return True
        elif self._next is not None:
            return self._next.process(event)
        return False

    @abstractmethod
    def match(self, event: 'Message') -> bool:
        raise NotImplementedError

    @abstractmethod
    def exec(self, event: telegram.TelegramObject):
        raise NotImplementedError

    @classmethod
    def str_alias(cls) -> str:
        if hasattr(cls, '__stralias__'):
            return cls.__stralias__

        class_name = cls.__name__
        if class_name.endswith('Command'):
            alias = class_name.removesuffix('Command')
        if class_name.endswith('Callback'):
            alias = class_name.removesuffix('Callback')

        return alias.lower()

    def require_auth(self) -> bool:
        return True


class CallbackHandler(Handler):

    def match(self, callbackquery: 'CallbackQuery'):
        func_name = callbackquery.function()
        if func_name != self.__class__.str_alias():
            return False
        return True

    @classmethod
    def build_callback_data(cls, **kwargs):
        args = urlencode(kwargs)
        data = '{}|{}'.format(cls.str_alias(), args)
        return data


class CommandHandler(Handler):

    def match(self, event: 'Message'):
        try:
            member = event.bot.get_chat_member(current_app.config['bot.group_id'], event.from_user.id)
            if member.status not in [telegram.ChatMember.MEMBER, telegram.ChatMember.ADMINISTRATOR, telegram.ChatMember.CREATOR]:
                return False
        except telegram.error.TelegramError:
            return False
        if not event.is_command() or event.command() != self.__class__.str_alias():
            return False
        return True


class GroupChatHandler(Handler):

    def match(self, event: 'Message'):
        if event.chat.id != current_app.config['bot.group_id']:
            return False
        if event.is_command():
            return False
        return True
