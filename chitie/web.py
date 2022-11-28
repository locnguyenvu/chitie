import collections
import hashlib
import chitie.config as hconfig
import hmac
import json
import sqlalchemy as sa
import telegram
import telegram.error

from .telegram import bot
from flask import (
    Flask,
    Blueprint,
    abort,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)
from urllib.parse import unquote
from .auth import user
from .expense import (
    Category as ExpenseCategory,
    Item as ExpenseItem,
    filter_expense
)
from .util import timerange


def _load_auth():
    if 'user_id' in session:
        g.user = user.find_by_id(session.get('user_id'))
    else:
        g.user = None


def login():
    botinfo = bot.get_me()
    callback_url = 'https://' + current_app.config['SERVER_NAME'] + '/tauth'
    return render_template('login.html', bot_username=botinfo.username, callback_url=callback_url)


def telegram_auth():
    query_params = request.args.to_dict()
    hash_check = query_params.pop('hash')
    sortParams = collections.OrderedDict(sorted(query_params.items()))
    message = "
".join(["{}={}".format(k, unquote(v)) for k, v in sortParams.items()])
    secret = hashlib.sha256(current_app.config.get('TELEGRAM_SECRET').encode('utf-8'))
    hash_message = hmac.new(secret.digest(), message.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
    if hash_check != hash_message:
        return abort(401)
    u = user.find_by_telegram_uid(query_params.get('id'))
    if hconfig.get('bot.group_type').value == telegram.Chat.SUPERGROUP and u is None:
        try:
            chatmember = bot.get_chat_member(hconfig.get('bot.group_id').value, query_params['id'])
            u = user.User(chatmember.user.username, chatmember.user.id)
            u.save()
        except telegram.error.TelegramError:
            pass
    if u is None or not u.is_active:
        error = 'Unknowed user'
        flash(error)
        return redirect(url_for('web.login'))
    session.clear()
    session['user_id'] = u.uuid
    return redirect(url_for('web.index'))


def login_required(view):
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('web.login'))
        return view(**kwargs)
    return wrapped_view


def index():
    tr = timerange.from_str(timerange.THIS_MONTH)
    items = ExpenseItem.query.filter(sa.and_(
        ExpenseItem.created_at >= tr.time_from,
        ExpenseItem.created_at <= tr.time_to
    )).all()
    group_by_cate = {}
    for item in items:
        if item.category_id not in group_by_cate:
            group_by_cate.setdefault(item.category_id, 0)
        group_by_cate[item.category_id] = group_by_cate[item.category_id] + item.amount
    categories = ExpenseCategory.query.filter(ExpenseCategory.id.in_(group_by_cate.keys())).all()
    chartdata = {}
    for cate in categories:
        chartdata.setdefault(cate.name, group_by_cate[cate.id])
    view_detail_url = url_for('web.list_expenses', time_from=tr.time_from.isoformat(), time_to=tr.time_to.isoformat())
    return render_template('index.html', chartdata=json.dumps(chartdata), view_detail_url=view_detail_url)


def list_expenses():
    expenses = filter_expense({
        'time_from': request.args.get('time_from', None),
        'time_to': request.args.get('time_to', None),
        'category_id': request.args.get('category_id', None),
    }, order_by_column='created_at', order_type='desc')
    return render_template('list_expenses.html', expenses=list(map(lambda e: e.to_dict(), expenses)))


def detail_expense(expense_id):
    expense = ExpenseItem.query.get(expense_id)
    categories = ExpenseCategory.query.all()
    errors = []
    if request.method == 'POST':
        update_info = {
            'subject': request.form.get('subject'),
            'amount': request.form.get('amount'),
            'category_id': request.form.get('category_id'),
            'transaction_type': request.form.get('transaction_type'),
        }
        for key, value in update_info.items():
            if value is None or len(value) == 0:
                errors.append(f'Invalid value for field *{key}*')
                continue
            setattr(expense, key, value)
        if int(expense.category_id) not in [cate.id for cate in categories]:
            errors.append('Invalid category')
        if len(errors) == 0:
            expense.save()
            return redirect(url_for('web.list_expenses'))

    return render_template('detail_expense.html', expense=expense, categories=categories, errors=errors)


def init_app(app: Flask):
    web = Blueprint('web', __name__)
    web.add_url_rule('/',
                     endpoint='index',
                     view_func=login_required(index))
    web.add_url_rule('/expenses',
                     endpoint='list_expenses',
                     view_func=login_required(list_expenses))
    web.add_url_rule('/expenses/<expense_id>',
                     endpoint='detail_expense',
                     methods=['GET', 'POST'],
                     view_func=login_required(detail_expense))
    web.add_url_rule('/login',
                     endpoint='login',
                     view_func=login)
    web.add_url_rule('/tauth',
                     endpoint='telegram_auth',
                     view_func=telegram_auth)
    web.before_request(_load_auth)
    app.register_blueprint(web)
    pass
