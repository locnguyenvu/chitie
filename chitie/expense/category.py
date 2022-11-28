import sqlalchemy as sa

from chitie.db import connection, ActiveRecord


class Category(connection.Model, ActiveRecord):

    __tablename__ = 'expense_categories'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    is_active = sa.Column(sa.Boolean, nullable=False)
    telegram_chat_id = sa.Column(sa.BigInteger(), nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=True)
    updated_at = sa.Column(sa.DateTime, nullable=True)

    def __init__(self, name):
        self.name = name
        self.is_active = True

    @classmethod
    def find(cls, chat_id, **kwargs):
        query = cls.query.filter_by(telegram_chat_id=chat_id)
        for key, value in kwargs.items():
            if not hasattr(cls, key):
                continue
            query = query.filter(getattr(cls, key) == value)
        return query.order_by(cls.name.asc()).all()
