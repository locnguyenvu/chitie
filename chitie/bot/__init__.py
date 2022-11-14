import os
import telegram
import chitie.config as hconfig

from flask import Flask, Blueprint, current_app, g, make_response, request, url_for
from chitie.auth.user import User
from chitie.i18n import t
from .dispatcher import chatmessage_handler, callbackquery_handler
from .ext import Bot, CallbackQuery, Message, get_chatcontext


bot = Bot(os.getenv("TELEGRAM_SECRET"))
webhook_secret = os.getenv('TELEGRAM_WEBHOOK_SECRET').strip()


def _before_webhook_request():
    configs = hconfig.get_bulk([
        'bot.group_id',
        'bot.group_type',
    ])
    for path, val in configs.items():
        if path in ['bot.group_id']:
            current_app.config[path] = int(val)
        else:
            current_app.config[path] = val
    update = telegram.Update.de_json(request.get_json(), bot)
    if update.message is not None:
        g.chatcontext = get_chatcontext(update.message)


def _setupbot(update: telegram.Update):
    """
    Setup when bot is promoted to Administrator of the first group
    """
    admin = User.query.first()
    if admin is not None:
        return
    if update.my_chat_member is None:
        return
    event = update.my_chat_member
    if event.new_chat_member.user.id != bot.id:
        return
    if event.new_chat_member.status != telegram.ChatMember.ADMINISTRATOR:
        return
    if event.chat.type not in [telegram.Chat.GROUP, telegram.Chat.SUPERGROUP]:
        return
    hconfig.set('bot.group_id', str(event.chat.id))
    hconfig.set('bot.group_type', event.chat.type)
    admin = User(event.from_user.username, event.from_user.id)
    admin.save()
    bot.send_message(event.chat.id, text=t('setup done'))


def listen_update(secret: str):
    if secret.strip() != webhook_secret:
        return make_response('Unauthorized', 401)
    update = telegram.Update.de_json(request.get_json(), bot)
    try:
        if 'bot.group_id' not in current_app.config:
            return _setupbot(update)

        if update.callback_query is not None:
            event = CallbackQuery.de_json(update.callback_query.to_dict(), bot)
            return callbackquery_handler.process(event)
        elif update.message is not None:
            event = Message.de_json(update.message.to_dict(), bot)
            return chatmessage_handler.process(event)
    except Exception as e:
        import traceback
        traceback.print_exc()
        msg = str(e)
        bot.talks(text=f'Error! {msg}')
    finally:
        return make_response('OK', 200)


def init_app(app: Flask):
    botbp = Blueprint('bot', __name__)
    botbp.add_url_rule("/tlg/<secret>", endpoint='callback', methods=['POST'], view_func=listen_update)
    botbp.before_request(_before_webhook_request)
    app.register_blueprint(botbp)
    bot.setWebhook(url_for('bot.callback', _external=True, _scheme='https', secret=os.getenv('TELEGRAM_WEBHOOK_SECRET')))
    g.bot = bot
    pass
