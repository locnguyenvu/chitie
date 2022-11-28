__all__ = [
    'bot',
]

from flask import Flask, current_app, g, url_for
from .shared import bot


def init_app(app: 'Flask'):
    g.telegram_bot = bot

    from .webhook import bp
    app.register_blueprint(bp)
    bot.setWebhook(url_for(
        'telegram.callback',
        _external=True,
        _scheme='https',
        secret=current_app.config['TELEGRAM_WEBHOOK_SECRET']))
