import sqlalchemy as sa

from chitie.db import connection, ActiveRecord
from chitie.exceptions import ExpenseItemIsInvalid
from chitie.i18n import t
from chitie.util import is_number
from .category import Category


TRANSACTION_TYPE_CREDIT = "credit"
TRANSACTION_TYPE_DEBIT = "debit"

CREDIT_AMOUNT_SYMBOL = 'c'


class Item(connection.Model, ActiveRecord):
    __tablename__ = "expense_items"

    id = sa.Column(sa.Integer, primary_key=True)
    subject = sa.Column(sa.String, nullable=False)
    amount = sa.Column(sa.Float(2), nullable=False)
    category_id = sa.Column(sa.Integer, nullable=True)
    transaction_type = sa.Column(sa.String, nullable=False)
    telegram_chat_id = sa.Column(sa.BigInteger, nullable=True)
    telegram_message_id = sa.Column(sa.BigInteger, nullable=True)
    updated_at = sa.Column(sa.DateTime, nullable=True)
    created_at = sa.Column(sa.DateTime, nullable=False)

    def save(self):
        self.amount = float(self.amount)
        if self.amount <= 0 or len(self.subject) == 0:
            raise ExpenseItemIsInvalid
        super().save()

    @classmethod
    def from_text(cls, text: str):
        item = cls()
        stripped_text = text.strip()
        chunks = stripped_text.split(' ')

        last_chunk = chunks[len(chunks) - 1].lower()
        if last_chunk.endswith(CREDIT_AMOUNT_SYMBOL):
            item.transaction_type = TRANSACTION_TYPE_CREDIT
        else:
            item.transaction_type = TRANSACTION_TYPE_DEBIT
        amount = last_chunk.removesuffix(CREDIT_AMOUNT_SYMBOL)
        if not is_number(amount):
            raise ExpenseItemIsInvalid
        if len(chunks[0:len(chunks) - 1]) == 0:
            raise ExpenseItemIsInvalid

        item.amount = float(amount)
        item.subject = ' '.join(chunks[0:len(chunks) - 1])
        return item

    def update_category(self, category_id: int):
        self.category_id = category_id
        self.save()

    def is_debit(self) -> bool:
        return self.transaction_type == TRANSACTION_TYPE_DEBIT

    def is_credit(self) -> bool:
        return self.transaction_type == TRANSACTION_TYPE_CREDIT

    def set_category(self, category: 'Category'):
        self.category_id = category.id
        self.category_name = category.name
        self._category = category

    @classmethod
    def find(cls, chat_id, conditions: dict, order_by_column=None, order_type="asc"):
        query = cls.query.filter_by(chat_id=chat_id)
        if conditions.get('time_from') is not None and conditions.get('time_to') is not None:
            query = query.filter(sa.and_(
                Item.created_at >= conditions['time_from'],
                Item.created_at <= conditions['time_to']
            ))
            del conditions['time_from']
            del conditions['time_to']

        for key in conditions:
            if not hasattr(Item, key) or conditions[key] is None or len(str(conditions[key])) == 0:
                continue
            query = query.filter(getattr(Item, key) == conditions[key])

        if order_by_column is not None:
            if order_type == "asc":
                query = query.order_by(getattr(Item, order_by_column).asc())
            elif order_type == "desc":
                query = query.order_by(getattr(Item, order_by_column).desc())

        expense_items = query.all()
        category_ids = list(set(map(lambda item: item.category_id, expense_items)))
        categories = Category.query.filter(Category.id.in_(category_ids)).all()
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
