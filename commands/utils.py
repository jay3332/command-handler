from __future__ import annotations

import inspect
import functools

from typing import Awaitable, Callable, TYPE_CHECKING, TypeVar, Union, overload

if TYPE_CHECKING:
    from typing_extensions import ParamSpec
    P = ParamSpec('P')
else:
    P = TypeVar('P')

R = TypeVar('R')

__all__ = (
    'ensure_async',
    'to_error_string'
)


@overload
def ensure_async(func: Callable[P, Awaitable[R]], /) -> Callable[P, Awaitable[R]]:
    ...


@overload
def ensure_async(func: Callable[P, R], /) -> Callable[P, Awaitable[R]]:
    ...


def ensure_async(func: Union[Callable[P, Awaitable[R]], Callable[P, R]], /) -> Callable[P, Awaitable[R]]:
    """Ensures that the given function is asynchronous.

    In other terms, if the function is already async, it will stay the same.
    Else, it will be converted into an async function. (Note that it will still be ran synchronously.)
    """
    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        maybe_coro = func(*args, **kwargs)

        if inspect.isawaitable(maybe_coro):
            return await maybe_coro

        return maybe_coro

    return wrapper


def to_error_string(exc: Exception, /) -> str:
    """Formats the given error into ``{error name}: {error text}``,
    e.g. ``ValueError: invalid literal for int() with base 10: 'a'``.

    If no error text exists, only the error name will be returned,
    e.g. just ``ValueError``.
    """
    if str(exc).strip():
        return '{0.__class__.__name__}: {0}'.format(exc)
    else:
        return exc.__class__.__name__
