from __future__ import absolute_import
from flask import Flask
import sys
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def create_app():
    app = Flask(__name__)
    # Flask config
    app.config['LOCALE'] = os.getenv("LOCALE", "vi_VN")
    app.config['PREFERRED_URL_SCHEME'] = os.getenv('PREFERRED_URL_SCHEME', 'https')
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev")
    app.config['SERVER_NAME'] = os.getenv('SERVER_NAME')
    app.config['SESSION_COOKIE_DOMAIN'] = os.getenv('SERVER_NAME')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    # Telegram config
    app.config['TELEGRAM_SECRET'] = os.getenv("TELEGRAM_SECRET")
    app.config['TELEGRAM_WEBHOOK_SECRET'] = os.getenv("TELEGRAM_WEBHOOK_SECRET")

    with app.app_context():
        from . import db, bot, config, web, cli
        db.init_app(app)
        config.load(app)
        bot.init_app(app)
        web.init_app(app)
        cli.init_app(app)

    return app


_ = create_app
