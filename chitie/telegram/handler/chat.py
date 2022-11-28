import telegram

from chitie.expense import (
    Category as ExpenseCategory
)
from chitie.i18n import t
from telegram.utils.helpers import escape_markdown

from ..ext import dispatcher
from ..ext.helper import (
    get_chatid,
    make_response,
)


dp = dispatcher()


@dp.chatcontext()
def on_addexpensecategory_insertname(msg):
    if len(ExpenseCategory.find(get_chatid(), name=msg.strip())) > 0:
        raise Exception(t('name existed, please try another'))
    category = ExpenseCategory(msg.strip())
    category.telegram_chat_id = get_chatid()
    category.save()

    categories = ExpenseCategory.find(get_chatid())
    index = 1
    category_str = []
    for cat in categories:
        if cat.id == category.id:
            category_str.append(f'{index}. {cat.name} (*)')
        else:
            category_str.append(f'{index}. {cat.name}')
        index = index + 1
    return make_response(
        escape_markdown("
".join([t('expense category') + ':', *category_str]), version=2),
        parse_mode=telegram.ParseMode.MARKDOWN_V2
    )


@dp.chatcontext()
def on_editexpensecategory_insertname(msg, id):
    if len(ExpenseCategory.find(get_chatid(), name=msg.strip())) > 0:
        raise Exception(t('name existed, please try another'))
    category = ExpenseCategory.query.get(id)
    old_name = category.name
    category.name = msg
    category.save()
    reply_text = "
".join([
        t('update success'),
        f'{old_name} -> {category.name}'
    ])
    return make_response(
        escape_markdown(reply_text, version=2),
        parse_mode=telegram.ParseMode.MARKDOWN_V2
    )


def on_addexpenseitem_insert(msg):
    return make_response('Hello, world')
