import telegram

from flask import Blueprint, current_app, g, make_response, request
from .shared import bot
from .handler import dp
from .ext.chatcontext import Chatcontext


bp = Blueprint('telegram', __name__)


@bp.route('/telegram/<secret>', methods=['POST'], endpoint='callback')
def callback(secret: str):
    if secret != current_app.config['TELEGRAM_WEBHOOK_SECRET']:
        return make_response('Unauthorized', 401)
    try:
        dp.dispatch(g.telegram_bot_update)
    except Exception as e:
        import traceback
        traceback.print_exc()
        msg = str(e)
        print(msg)
    finally:
        return make_response('OK', 200)


@bp.before_request
def _before():
    update = telegram.Update.de_json(request.get_json(), bot)

    g.telegram_bot = bot
    g.telegram_bot_update = update
    g.telegram_bot_chatcontext = Chatcontext.query.filter_by(
        chat_id=update.effective_chat.id,
        user_id=update.effective_user.id,
        is_active=True
    ).order_by(Chatcontext.created_at.asc()).first()
