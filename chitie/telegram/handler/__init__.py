from ..ext import dispatcher
from .command import dp as command_dp
from .callbackquery import dp as callbackquery_dp
from .chat import (
    dp as chat_dp,
    on_addexpenseitem_insert
)

# Load handler pacakges
_ = command_dp
_ = callbackquery_dp
_ = chat_dp


dp = dispatcher()
dp.default_handler_func = on_addexpenseitem_insert
