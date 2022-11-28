import telegram

from flask import current_app


bot = telegram.Bot(current_app.config['TELEGRAM_SECRET'])
