import telegram

from chitie.i18n import t
from chitie.expense import (
    Category as ExpenseCategory
)
from .callbackquery import (
    expense_category_add,
    expense_category_viewdetail,

    inlinekeyboardbutton_close,
)
from ..ext.dispatcher import dispatcher
from ..ext.helper import (
    build_inlinekeyboardbutton,
    get_chatid,
    make_response
)


dp = dispatcher()


@dp.command('start')
def start_command():
    return make_response('Hi there!')


@dp.command('category')
def category_command():
    categories = ExpenseCategory.find(get_chatid())
    category_btns = [
        [build_inlinekeyboardbutton(cat.name, expense_category_viewdetail, id=cat.id)]
        for cat in categories
    ]
    buttons = [
        build_inlinekeyboardbutton(t('add'), expense_category_add),
        build_inlinekeyboardbutton(t('close'), inlinekeyboardbutton_close)
    ]
    return make_response('Expense categories', reply_markup=telegram.InlineKeyboardMarkup([*category_btns, buttons]))


@dp.command('review')
def review_command(msg):
    return make_response(msg)
