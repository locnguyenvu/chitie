import telegram
import chitie.config as hconfig

from chitie.auth.user import User
from chitie.exceptions import ExpenseItemIsInvalid
from chitie.expense import (
    ExpenseItem,
    recommend_expense_category,
)
from chitie.i18n import t
from flask import current_app, g
from .ext import (
    GroupChatHandler,
    Message
)
from .callback import (
    SelectExpenseCategoryCallback,
    ShowMoreExpenseCategoryCallback,
    AddExpenseCategoryCallback
)


class NewJoinUser(GroupChatHandler):

    def match(self, message: Message) -> bool:
        if message.new_chat_members is None or len(message.new_chat_members) == 0:
            return False
        return super().match(message)

    def exec(self, event: Message):
        for us in event.new_chat_members:
            nu = User.query.filter_by(telegram_userid=us.id).first()
            if nu is None:
                nu = User(us.username, us.id)
            nu.is_active = True
            nu.save()
            pass
        if event.chat.id != current_app.config['bot.group_id']:
            hconfig.set('bot.group_id', str(event.chat.id))


class LeftUser(GroupChatHandler):

    def match(self, message: Message) -> bool:
        if message.left_chat_member is None:
            return False
        return super().match(message)

    def exec(self, event: Message):
        u = User.query.filter_by(telegram_userid=event.left_chat_member.id).first()
        if u is not None:
            u.is_active = False
            u.save()


class CommandInputContext(GroupChatHandler):

    def match(self, message: 'Message') -> bool:
        if 'chatcontext' in g and g.chatcontext is None:
            return False
        return super().match(message)

    def exec(self, event: Message):
        g.chatcontext.process(event)


class AddExpenseItem(GroupChatHandler):

    def match(self, message: Message):
        if 'chatcontext' in g and g.chatcontext is not None:
            return False
        if message.text is None or len(message.text.strip()) == 0:
            return False
        return super().match(message)

    def exec(self, event: Message):
        try:
            item = ExpenseItem.from_text(event.text)
            item.telegram_message_id = event.message_id
            item.telegram_chat_id = event.chat.id
            item.save()
        except ExpenseItemIsInvalid:
            event.bot.send_message(event.chat.id, t('invalid format'))
            return

        categories, op = recommend_expense_category(item.subject)
        if len(categories) > 0:
            buttons = [
                [
                    telegram.InlineKeyboardButton(
                        f"{category.name}",
                        callback_data=SelectExpenseCategoryCallback.build_callback_data(item_id=item.id, category_id=category.id))
                ]
                for category in categories
            ]
            if op:
                buttons.append([
                    telegram.InlineKeyboardButton(
                        "...",
                        callback_data=ShowMoreExpenseCategoryCallback.build_callback_data(item_id=item.id))
                ])
            else:
                buttons.append([
                    telegram.InlineKeyboardButton(
                        t('add'),
                        callback_data=AddExpenseCategoryCallback.build_callback_data(item_id=item.id))
                ])
        else:
            buttons = [
                [
                    telegram.InlineKeyboardButton(
                        t('add'),
                        callback_data=AddExpenseCategoryCallback.build_callback_data(item_id=item.id))
                ]
            ]
        event.bot.send_message(event.chat.id, t('select category'), reply_markup=telegram.InlineKeyboardMarkup(buttons))
        pass
