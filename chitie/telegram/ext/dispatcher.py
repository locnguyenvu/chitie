import inspect
import telegram
import typing as t

from urllib.parse import parse_qs, urlencode, urlparse
from .helper import (
    get_chatcontext,
    make_response,
)


CALLBACKQUERY = 'callbackquery'
CHATCONTEXT = 'chatcontext'
COMMAND = 'command'


def _add_urlargument(url: str, **kwargs) -> str:
    route = urlparse(url)

    urlargs = {}
    if len(route.query) > 0:
        for key, value in parse_qs(route.query).items():
            if len(value) > 1:
                urlargs.setdefault(key, value)
            else:
                urlargs.setdefault(key, value[0])
    for key, value in kwargs.items():
        urlargs[key] = value
    return f'{route.path}?' + urlencode(urlargs)


def _get_route(update: 'telegram.Update') -> str:
    if update.callback_query is not None:
        return f'{CALLBACKQUERY}/{update.callback_query.data}'
    if update.message is not None:
        if isinstance(update.message.entities, list):
            command_entities = list(filter(lambda ent: ent.type == telegram.MessageEntity.BOT_COMMAND, update.message.entities))
            if len(command_entities) > 0:
                fmatch = command_entities[0]
                command = update.message.text[fmatch.offset:fmatch.length + fmatch.offset].lstrip('/')
                arguments = update.message.text[fmatch.offset + fmatch.length:]
                return f'{COMMAND}/{command}?' + urlencode(dict(msg=arguments))
        chatcontext = get_chatcontext()
        if chatcontext is None:
            return ''
        return f'{CHATCONTEXT}/' + _add_urlargument(chatcontext.callbackdata, msg=update.message.text)


class dispatcher(object):

    routes = {}

    default_handler_func = None

    def __init__(self):
        pass

    def command(self, name, description: str = ''):
        def decorator(f: t.Callable):
            self.add_route(COMMAND, name, f, description)
        return decorator

    def callback_query(self):
        def decorator(f: t.Callable):
            name = f.__name__
            self.add_route(CALLBACKQUERY, name, f)
            return f
        return decorator

    def chatcontext(self):
        def decorator(f: t.Callable):
            name = f.__name__
            self.add_route(CHATCONTEXT, name, f)
            return f
        return decorator

    def add_route(self, rtype: str, name: str, handler_func: t.Callable, description: str = ''):
        if rtype not in [CALLBACKQUERY, CHATCONTEXT, COMMAND]:
            raise ValueError()
        route = f'{rtype}/{name}'
        self.routes.setdefault(route, dict(handler_func=handler_func, description=description))

    def dispatch(self, update: 'telegram.Update'):
        route = urlparse(_get_route(update))
        import rich
        rich.print(route)
        handler_func = self.default_handler_func
        for rt, elem in self.routes.items():
            if rt == route.path:
                handler_func = elem['handler_func']
                break

        if handler_func is None:
            return

        try:
            func_arginspect = inspect.getfullargspec(handler_func)
            if (func_arginspect.args) == 0:
                handler_func()
                return

            kwargs = {}
            if len(route.query) > 0:
                for key, value in parse_qs(route.query).items():
                    if len(value) > 1:
                        kwargs.setdefault(key, value)
                    else:
                        kwargs.setdefault(key, value[0])

            args = []
            for argname in func_arginspect.args:
                if argname in kwargs:
                    args.append(kwargs[argname])
                    del kwargs[argname]
                else:
                    args.append(None)
            if func_arginspect.varkw is None:
                handler_func(*args)
            else:
                handler_func(*args, **kwargs)

            """
            Chat context is only available with single message
            """
            context = get_chatcontext()
            if context is not None:
                context.delete()
            return
        except Exception as e:
            import traceback
            traceback.print_exc()
            make_response(str(e))
