import telegram

from chitie.expense import (
    Category as ExpenseCategory
)
from chitie.i18n import t
from telegram.utils.helpers import escape_markdown

from .chat import (
    on_addexpensecategory_insertname,
    on_editexpensecategory_insertname,
)
from ..ext import dispatcher
from ..ext.helper import (
    build_inlinekeyboardbutton,
    delete_current_message,
    edit_current_message,
    get_userid,
    get_chatid
)
from ..ext.chatcontext import Chatcontext


dp = dispatcher()


@dp.callback_query()
def inlinekeyboardbutton_close():
    delete_current_message()


@dp.callback_query()
def expense_category_add():
    delete_current_message()
    context = Chatcontext(get_chatid(), get_userid(), on_addexpensecategory_insertname)
    context.save()
    return


@dp.callback_query()
def expense_category_showlist():
    categories = ExpenseCategory.find(get_chatid())
    category_btns = [
        [build_inlinekeyboardbutton(cat.name, expense_category_viewdetail, id=cat.id)]
        for cat in categories
    ]
    buttons = [
        build_inlinekeyboardbutton(t('add'), expense_category_add),
        build_inlinekeyboardbutton(t('close'), inlinekeyboardbutton_close)
    ]
    return edit_current_message('Expense categories', reply_markup=telegram.InlineKeyboardMarkup([*category_btns, buttons]))


@dp.callback_query()
def expense_category_viewdetail(id: int):
    category = ExpenseCategory.query.get(id)
    message = "
".join([
        f"{category.name}",
        f"Status: {category.is_active}",
    ])
    action_buttons = [
        build_inlinekeyboardbutton(t('edit name'), expense_category_editname, id=category.id),
        build_inlinekeyboardbutton(
            t('activate') if not category.is_active else t('deactivate'),
            expense_category_togglestatus, id=category.id)
    ]
    nav_buttons = [
        build_inlinekeyboardbutton(t('back'), expense_category_showlist),
        build_inlinekeyboardbutton(t('close'), inlinekeyboardbutton_close)
    ]
    edit_current_message(escape_markdown(message),
                         reply_markup=telegram.InlineKeyboardMarkup([action_buttons, nav_buttons]),
                         parse_mode=telegram.ParseMode.MARKDOWN_V2)


@dp.callback_query()
def expense_category_editname(id: int):
    category = ExpenseCategory.query.get(id)
    if category is None:
        raise Exception(t('category does not exist'))
    edit_current_message(f'Change name of category {category.name}')
    context = Chatcontext(get_chatid(), get_userid(), on_editexpensecategory_insertname, id=category.id)
    context.save()


@dp.callback_query()
def expense_category_togglestatus(id: int):
    category = ExpenseCategory.query.get(id)
    if category is None:
        raise Exception(t('category does not exist'))
    if category.is_active:
        category.is_active = False
    else:
        category.is_active = True
    category.save()
    message = "
".join([
        f"{category.name}",
        f"Status: {category.is_active}",
    ])
    action_buttons = [
        build_inlinekeyboardbutton(t('edit name'), expense_category_editname, id=category.id),
        build_inlinekeyboardbutton(
            t('activate') if not category.is_active else t('deactivate'),
            expense_category_togglestatus, id=category.id)
    ]
    nav_buttons = [
        build_inlinekeyboardbutton(t('back'), expense_category_showlist),
        build_inlinekeyboardbutton(t('close'), inlinekeyboardbutton_close)
    ]
    edit_current_message(escape_markdown(message),
                         reply_markup=telegram.InlineKeyboardMarkup([action_buttons, nav_buttons]),
                         parse_mode=telegram.ParseMode.MARKDOWN_V2)
