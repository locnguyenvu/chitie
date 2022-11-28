import inspect
import sqlalchemy as sa
import typing as t

from urllib.parse import urlencode
from chitie.db import connection, ActiveRecord


class Chatcontext(connection.Model, ActiveRecord):

    __tablename__ = 'telegram_chatcontexts'

    id = sa.Column(sa.Integer, primary_key=True)
    chat_id = sa.Column(sa.Integer, nullable=False)
    user_id = sa.Column(sa.Integer, nullable=False)
    callbackdata = sa.Column(sa.Text, nullable=False)
    is_active = sa.Column(sa.Boolean, nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=True)

    def __init__(self, chat_id: int, user_id: int, callback: t.Callable, **kwargs):
        callback_name = callback.__name__
        callback_arginspect = inspect.getfullargspec(callback)
        callback_args = {}
        for argname in callback_arginspect.args:
            callback_args.setdefault(argname, None)
            if argname in kwargs:
                callback_args[argname] = kwargs[argname]
        self.callbackdata = f'{callback_name}?' + urlencode(callback_args)
        self.chat_id = chat_id
        self.user_id = user_id
        self.is_active = True

    def delete(self):
        self.query.session.delete(self)
        self.query.session.commit()
