from typing import List
from .callback import (
    SelectExpenseCategoryCallback,
    ShowMoreExpenseCategoryCallback,
    ViewDetailExpenseCategoryCallback,
    ToggleActiveExpenseCategoryCallback,
    ListExpenseCategoryCallback,
    EditExpenseCategoryNameCallback,
    CloseButtonCallback,
    AddExpenseCategoryCallback,
)
from .command import (
    SetupCommand,
    ReviewCommand,
    WebCommand,
    CategoryCommand,
    CancelCommand
)
from .ext import Handler
from .group import (
    NewJoinUser,
    LeftUser,
    CommandInputContext,
    AddExpenseItem
)


def _build_chain(*args: List['Handler']) -> 'Handler':
    first = current = args[0]
    for i in range(1, len(args)):
        current = current.set_next(args[i])
    return first


chatmessage_handler = _build_chain(
    SetupCommand(),
    ReviewCommand(),
    WebCommand(),
    CategoryCommand(),
    CancelCommand(),
    NewJoinUser(),
    LeftUser(),
    CommandInputContext(),
    AddExpenseItem()
)
callbackquery_handler = _build_chain(
    SelectExpenseCategoryCallback(),
    ShowMoreExpenseCategoryCallback(),
    ViewDetailExpenseCategoryCallback(),
    ToggleActiveExpenseCategoryCallback(),
    ListExpenseCategoryCallback(),
    CloseButtonCallback(),
    AddExpenseCategoryCallback(),
    EditExpenseCategoryNameCallback(),
)
