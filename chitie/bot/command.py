import os
import telegram
import chitie.config as chitie_config
import chitie.auth.user as user

from flask import url_for, g
from chitie.i18n import t
from chitie.util import timerange
from chitie.expense import (
    ExpenseCategory,
    filter_expense
)
from .ext import (
    CommandHandler,
    Message
)
from .callback import (
    ViewDetailExpenseCategoryCallback,
    AddExpenseCategoryCallback,
    CloseButtonCallback,
)


class SetupCommand(CommandHandler):
    def require_auth(self) -> bool:
        return False

    def exec(self, event: Message):
        if event.chat.type not in [telegram.Chat.GROUP, telegram.Chat.SUPERGROUP]:
            return
        admin = user.User.query.first()
        secret = event.argumentstr()
        if admin is None:
            if os.getenv('TELEGRAM_WEBHOOK_SECRET') != secret:
                event.bot.send_message(event.chat.id, 'Unauthorized!')
                return
            admin = user.User(event.from_user.username, event.from_user.id)
            admin.save()
        chitie_config.set('bot.group_id', str(event.chat.id))
        chitie_config.set('bot.group_type', event.chat.type)
        event.bot.send_message(event.chat.id, t('setup done'))


class ReviewCommand(CommandHandler):
    def exec(self, event: Message):
        if len(event.argumentstr()) == 0:
            tr = timerange.from_str('this month')
        else:
            tr = timerange.from_str(event.argumentstr())
        if tr.time_from is None or tr.time_to is None:
            raise ValueError('Invalide date')
        records = filter_expense({'time_from': tr.time_from, 'time_to': tr.time_to})
        debit_amount = 0
        credit_amount = 0
        total_amount = 0
        for r in records:
            if r.is_credit():
                credit_amount += r.amount
            if r.is_debit():
                debit_amount += r.amount

            total_amount += r.amount

        maxlength = 0
        for amount in [debit_amount, credit_amount, total_amount]:
            if maxlength < len(f'{amount:,}'):
                maxlength = len(f'{amount:,}')

        content = "\n".join([
            "```",
            f'{"d":2}| {debit_amount:>{maxlength},}',
            f'{"c":2}| {credit_amount:>{maxlength},}',
            f'{"-":->{maxlength + 4}}',
            f'{"t":2}| {total_amount:>{maxlength},}',
            "```",
        ])
        event.bot.send_message(event.chat.id, text=content, parse_mode=telegram.ParseMode.MARKDOWN_V2)


class WebCommand(CommandHandler):
    def exec(self, event: Message):
        event.bot.unpin_all_chat_messages(event.chat.id)
        reply_markup = telegram.InlineKeyboardMarkup([
            [
                telegram.InlineKeyboardButton(
                    "Open",
                    login_url=telegram.LoginUrl(url_for('web.telegram_auth', _external=True, _scheme='https')),
                )
            ]
        ])
        event.bot.send_message(event.chat.id, 'Web', reply_markup=reply_markup, parse_mode=telegram.ParseMode.HTML)


class CategoryCommand(CommandHandler):

    def exec(self, event: 'Message'):
        categories = ExpenseCategory.query.order_by(ExpenseCategory.name.asc()).all()
        buttons = [
            [
                telegram.InlineKeyboardButton(
                    cat.name,
                    callback_data=ViewDetailExpenseCategoryCallback.build_callback_data(category_id=cat.id))
            ]
            for cat in categories
        ]
        buttons.append([
            telegram.InlineKeyboardButton(t('add'), callback_data=AddExpenseCategoryCallback.build_callback_data()),
            telegram.InlineKeyboardButton(t('close'), callback_data=CloseButtonCallback.build_callback_data())
        ])
        event.bot.send_message(event.chat.id, t('expense categories'), reply_markup=telegram.InlineKeyboardMarkup(buttons))


class CancelCommand(CommandHandler):
    def exec(self, event: 'Message'):
        if 'chatcontext' in g and g.chatcontext is not None:
            chatcontext = g.chatcontext
            chatcontext.is_active = False
            chatcontext.save()
