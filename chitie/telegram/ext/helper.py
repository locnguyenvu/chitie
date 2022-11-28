import inspect
import telegram
import typing as t

from flask import g
from urllib.parse import urlencode

from .chatcontext import Chatcontext
from ..shared import bot


def get_update() -> 'telegram.Update':
    if 'telegram_bot_update' not in g:
        raise ValueError('telegram_bot_update')
    return g.telegram_bot_update


def get_chatid() -> t.Union[None, int]:
    update = get_update()
    return update.effective_chat.id


def get_userid() -> int:
    update = get_update()
    return update.effective_user.id


def get_chatcontext() -> t.Union[None, 'Chatcontext']:
    if 'telegram_bot_chatcontext' not in g:
        raise ValueError('telegram_bot_chatcontext')
    return g.telegram_bot_chatcontext


def make_response(text, *args, **kwargs):
    update = get_update()
    bot.send_message(update.effective_message.chat_id, text, *args, **kwargs)


def edit_current_message(text, *args, **kwargs):
    update = get_update()
    update.effective_message.edit_text(text, *args, **kwargs)


def delete_current_message():
    update = get_update()
    update.effective_message.delete()


def build_callbackquery_data(f: t.Callable, **kwargs) -> str:
    func_name = f.__name__
    func_arginspect = inspect.getfullargspec(f)
    func_kwargs = {}
    if len(func_arginspect.args) > 0:
        for argname in func_arginspect.args:
            func_kwargs.setdefault(argname, None)
            if argname not in kwargs:
                raise Exception(f'Argument {argname} is missing!')
            if argname in kwargs:
                func_kwargs[argname] = kwargs[argname]
    return f'{func_name}?' + urlencode(func_kwargs)


def build_inlinekeyboardbutton(text: str, handle_func: t.Callable, **kwargs) -> 'telegram.InlineKeyboardButton':
    return telegram.InlineKeyboardButton(
        text,
        callback_data=build_callbackquery_data(handle_func, **kwargs)
    )
