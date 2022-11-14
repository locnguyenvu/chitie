import telegram

from chitie.expense import (
    ExpenseItem,
    ExpenseCategory,
)
from chitie.i18n import t
from telegram.utils.helpers import escape_markdown
from .ext import (
    CallbackQuery,
    CallbackHandler
)
from .chatcontext import (
    Chatcontext,
    EditExpenseCategoryName,
    AddExpenseCategory
)


class SelectExpenseCategoryCallback(CallbackHandler):
    def exec(self, event: CallbackQuery):
        args = event.arguments()
        item = ExpenseItem.query.get(int(args['item_id']))
        item.update_category(int(args['category_id']))
        category = ExpenseCategory.query.get(item.category_id)
        event.edit_message_text(f'> {category.name}')
        return True


class ShowMoreExpenseCategoryCallback(CallbackHandler):
    def exec(self, event: CallbackQuery):
        args = event.arguments()

        categories = ExpenseCategory.query.filter_by(is_active=True).all()
        buttons = [
            [
                telegram.InlineKeyboardButton(
                    f"{category.name}",
                    callback_data=SelectExpenseCategoryCallback.build_callback_data(item_id=args['item_id'], category_id=category.id))
            ]
            for category in categories
        ]
        buttons.append([
            telegram.InlineKeyboardButton(
                t('add'),
                callback_data=AddExpenseCategoryCallback.build_callback_data(item_id=args['item_id']))
        ])
        event.edit_message_text(t('select category'), reply_markup=telegram.InlineKeyboardMarkup(buttons))
        return True


class CloseButtonCallback(CallbackHandler):

    def exec(self, event: CallbackHandler):
        event.delete_message()


class ListExpenseCategoryCallback(CallbackHandler):

    def exec(self, event: CallbackQuery):
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
            telegram.InlineKeyboardButton(t('close'), callback_data=CloseButtonCallback.build_callback_data()),
        ])
        event.edit_message_text(t('expense categories'), reply_markup=telegram.InlineKeyboardMarkup(buttons))


class ViewDetailExpenseCategoryCallback(CallbackHandler):

    def exec(self, event: CallbackQuery):
        args = event.arguments()

        category = ExpenseCategory.query.get(args['category_id'])
        content = [
            f"{category.name}",
            "{}: {}".format(t('active'), str(category.is_active))
        ]
        buttons = [
            [
                telegram.InlineKeyboardButton(
                    t('change name'),
                    callback_data=EditExpenseCategoryNameCallback.build_callback_data(category_id=category.id)),
            ], [
                telegram.InlineKeyboardButton(
                    t('deactivate') if category.is_active else t('activate'),
                    callback_data=ToggleActiveExpenseCategoryCallback.build_callback_data(category_id=category.id))
            ], [
                telegram.InlineKeyboardButton(
                    t('back'),
                    callback_data=ListExpenseCategoryCallback.build_callback_data())
            ]
        ]
        event.edit_message_text(escape_markdown("\n".join(content)), reply_markup=telegram.InlineKeyboardMarkup(buttons), parse_mode=telegram.ParseMode.MARKDOWN_V2)


class ToggleActiveExpenseCategoryCallback(CallbackHandler):

    def exec(self, event: CallbackQuery):
        args = event.arguments()
        category = ExpenseCategory.query.get(args['category_id'])
        category.is_active = True if not category.is_active else False
        category.save()

        content = [
            f"**{category.name}**",
            "{}: {}".format(t('active'), str(category.is_active))
        ]
        buttons = [
            [telegram.InlineKeyboardButton(t('back'), callback_data=ListExpenseCategoryCallback.build_callback_data())],
            [telegram.InlineKeyboardButton(t('close'), callback_data=CloseButtonCallback.build_callback_data())]
        ]
        event.edit_message_text("\n".join(content), reply_markup=telegram.InlineKeyboardMarkup(buttons), parse_mode=telegram.ParseMode.MARKDOWN_V2)


class EditExpenseCategoryNameCallback(CallbackHandler):

    def exec(self, event: 'CallbackQuery'):
        args = event.arguments()
        Chatcontext.new(event.message.chat.id, event.from_user.id, EditExpenseCategoryName, **args)
        event.edit_message_text(t('enter new name'))


class AddExpenseCategoryCallback(CallbackHandler):

    def exec(self, event: 'CallbackQuery'):
        args = event.arguments()
        Chatcontext.new(event.message.chat.id, event.from_user.id, AddExpenseCategory, **args)
        event.edit_message_text(t('enter category name'))
