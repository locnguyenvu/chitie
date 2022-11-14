import sqlalchemy as sa

from click import echo
from chitie.db import connection, ActiveRecord


class Category(connection.Model, ActiveRecord):

    __tablename__ = 'expense_categories'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    is_active = sa.Column(sa.Boolean, nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=True)
    updated_at = sa.Column(sa.DateTime, nullable=True)

    def __init__(self, name):
        self.name = name
        self.is_active = True


def add(name: str):
    existed = Category.query.filter_by(name=name).first()
    if existed is not None:
        echo('[!] Error - This category has already existed')
        return
    cat = Category(name)
    cat.save()
    return cat


def list():
    rows = Category.query.filter_by(is_active=True).order_by(Category.id).all()
    return rows
