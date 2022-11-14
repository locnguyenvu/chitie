__all__ = [
    'ExpenseCategory',
    'ExpenseItem',
    'filter_expense',
    'recommend_expense_category'
]
import datedelta
import datetime
import sqlalchemy as sa

from chitie.i18n import t
from .item import (
    Item as ExpenseItem,
)
from .category import (
    Category as ExpenseCategory,
)


def recommend_expense_category(subject: str):
    first_word = subject.split(' ')[0]
    search_from = datetime.datetime.now() - (5 * datedelta.WEEK)
    query = ExpenseItem.query.with_entities(ExpenseItem.category_id)
    query = query.filter(ExpenseItem.subject.like(f'%{first_word}%'))
    query = query.filter(ExpenseItem.created_at >= search_from.replace(hour=0, minute=0, second=0)).group_by(ExpenseItem.category_id)
    histories = query.limit(5).all()
    if len(histories) == 0 or histories[0][0] is None:
        return ExpenseCategory.query.filter_by(is_active=True).all(), False
    return ExpenseCategory.query.filter(ExpenseCategory.id.in_([item[0] for item in histories])).all(), True


def filter_expense(conditions: dict, order_by_column=None, order_type="asc"):
    query = ExpenseItem.query
    if conditions.get('time_from') is not None and conditions.get('time_to') is not None:
        query = query.filter(sa.and_(
            ExpenseItem.created_at >= conditions['time_from'],
            ExpenseItem.created_at <= conditions['time_to']
        ))
        del conditions['time_from']
        del conditions['time_to']

    for key in conditions:
        if not hasattr(ExpenseItem, key) or conditions[key] is None or len(str(conditions[key])) == 0:
            continue
        query = query.filter(getattr(ExpenseItem, key) == conditions[key])

    if order_by_column is not None:
        if order_type == "asc":
            query = query.order_by(getattr(ExpenseItem, order_by_column).asc())
        elif order_type == "desc":
            query = query.order_by(getattr(ExpenseItem, order_by_column).desc())

    expense_items = query.all()
    category_ids = list(set(map(lambda item: item.category_id, expense_items)))
    categories = ExpenseCategory.query.filter(ExpenseCategory.id.in_(category_ids)).all()
    category_map = {}
    for cate in categories:
        category_map.setdefault(cate.id, cate)

    result = []
    for item in expense_items:
        if item.category_id is not None:
            item.set_category(category_map[item.category_id])
        else:
            item.category_name = t('unknown')
            item.category_id = 0
        result.append(item)

    return result
