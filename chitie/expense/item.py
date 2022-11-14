import sqlalchemy as sa

from chitie.db import connection, ActiveRecord
from chitie.exceptions import ExpenseItemIsInvalid
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
