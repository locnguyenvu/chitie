import sqlalchemy as sa

from flask import Flask
from datetime import datetime
from chitie.db import connection, ActiveRecord


class Config(connection.Model, ActiveRecord):

    INTVALUE = ['bot.group_id']

    __tablename__ = "configs"

    id = sa.Column(sa.Integer, primary_key=True)
    path = sa.Column(sa.String, nullable=False)
    value = sa.Column(sa.String, nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=True)
    updated_at = sa.Column(sa.DateTime, nullable=True)


def load(app: Flask):
    records = Config.query.all()
    for reco in records:
        app.config[reco.path] = reco.value


def get(key: str):
    return Config.query.filter_by(path=key).first()


def get_bulk(keys: list) -> dict:
    resultset = Config.query.filter(Config.path.in_(keys)).all()
    configs = {}
    for row in resultset:
        configs[row.path] = row.value
    return configs


def set(key: str, value):
    config = Config.query.filter_by(path=key).first()
    if not config:
        config = Config()
        config.path = key
        config.created_at = datetime.now()
    config.value = str(value)
    config.updated_at = datetime.now()
    config.save()
