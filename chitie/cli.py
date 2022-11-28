from click import Command
from flask import Flask
from flask.cli import with_appcontext

from .telegram import bot


def bot_set_commands():
    bot.set_my_commands([
        ('category', 'List categories'),
        ('review', 'Review expense in time range'),
        ('web', 'Web button')
    ])


def init_app(app: 'Flask'):
    app.cli.add_command(
        Command(
            'bot:set_commands',
            callback=with_appcontext(bot_set_commands)
        )
    )
