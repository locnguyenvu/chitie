import abc
import importlib
import inspect
import sqlalchemy as sa

from chitie.db import connection, ActiveRecord
from chitie.expense import ExpenseCategory, ExpenseItem
from chitie.i18n import t
from telegram import Message


class Chatcontext(connection.Model, ActiveRecord):

    __tablename__ = 'bot_chatcontexts'

    id = sa.Column(sa.Integer, primary_key=True)
    chat_id = sa.Column(sa.Integer, nullable=False)
    user_id = sa.Column(sa.Integer, nullable=False)
    serialized_handler = sa.Column(sa.JSON, nullable=False)
    is_active = sa.Column(sa.Boolean, nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=True)

    @sa.orm.reconstructor
    def __init_on_load(self):
        mod = importlib.import_module(self.serialized_handler["module_path"])
        handler = getattr(mod, self.serialized_handler["class_name"])
        self._handler = handler(**self.serialized_handler["arguments"])
        pass

    def process(self, message: 'Message'):
        if self._handler is None:
            return
        try:
            self._handler.exec(message)
            self.is_active = False
            self.save()
        except Exception as error:
            message.bot.send_message(message.chat.id, str(error))

    def __init__(self, handler: 'ContextHandler'):
        self._handler = handler
        self.is_active = True

    def save(self):
        self.serialized_handler = self._handler.serialize()
        super().save()

    @classmethod
    def new(cls, chat_id, user_id, handler_type, **kwargs):
        handler = handler_type(**kwargs)
        instance = cls(handler)
        instance.chat_id = chat_id
        instance.user_id = user_id
        instance.save()


class ContextHandler:

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def serialize(self):
        inspect_constructor = inspect.getargspec(self.__class__.__init__)
        construct_arguments = inspect_constructor[0]

        args = []
        for argkw in construct_arguments[1:]:
            args.append(getattr(self, argkw))

        return {
            "module_path": self.__class__.__module__,
            "class_name": self.__class__.__name__,
            "arguments": self.__dict__
        }

    @abc.abstractmethod
    def exec(self, message: 'Message'):
        raise NotImplementedError


class EditExpenseCategoryName(ContextHandler):

    def exec(self, message: 'Message'):
        cate = ExpenseCategory.query.get(self.category_id)
        if cate is None:
            return
        new_name = message.text.strip()
        existed = ExpenseCategory.query.filter_by(name=new_name).first()
        if existed is not None:
            raise ValueError(t('name existed, try another one'))
        old_name = cate.name
        cate.name = message.text.strip()
        cate.save()

        message.bot.send_message(message.chat.id, f'{old_name} -> {cate.name}')


class AddExpenseCategory(ContextHandler):

    def exec(self, message: 'Message'):
        name = message.text.strip()
        existed = ExpenseCategory.query.filter_by(name=name).first()
        if existed is not None:
            raise ValueError(t('name existed, try another one'))
        cate = ExpenseCategory(name)
        cate.save()
        if hasattr(self, 'item_id'):
            item = ExpenseItem.query.get(self.item_id)
            item.update_category(cate.id)
            message.bot.send_message(message.chat.id, f"{item.subject} > {cate.name}")
        else:
            categories = ExpenseCategory.query.order(ExpenseCategory.name.asc()).all()
            message.bot.send_message(message.chat.id, "\n".join(["Categories:"] + [f"- {cate.name}" for cate in categories]))
