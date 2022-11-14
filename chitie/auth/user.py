import sqlalchemy as sa
import uuid

from chitie.db import connection, ActiveRecord


class User(connection.Model, ActiveRecord):
    __tablename__ = "users"

    uuid = sa.Column(sa.String, nullable=False, unique=True, primary_key=True)
    telegram_username = sa.Column(sa.String, nullable=False)
    telegram_userid = sa.Column(sa.Integer, nullable=False)
    is_active = sa.Column(sa.Boolean, nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=False)

    def __init__(self, tlg_username, tlg_userid):
        id = uuid.uuid4()
        self.uuid = str(id)
        self.telegram_userid = int(tlg_userid)
        self.telegram_username = tlg_username
        self.is_active = True


def find_by_id(id):
    return User.query.filter_by(uuid=id).first()


def find_by_telegram_uid(uid):
    row = User.query.filter_by(telegram_userid=uid).first()
    return row
