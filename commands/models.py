from __future__ import annotations

from inspect import iscoroutinefunction

from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Sequence,
    Tuple,
    TYPE_CHECKING,
    TypeVar,
)

R = TypeVar('R')

if TYPE_CHECKING:
    from typing_extensions import Concatenate, ParamSpec

    P = ParamSpec('P')
    CommandCallback = Callable[Concatenate['Context', P], Awaitable[R]]
    ErrorCallback = Callable[['Context', Exception], Awaitable[Any]]
else:
    P = TypeVar('P')


def _temporary_dispatch(event: str, *args, **kwargs) -> None:
    print(f'[DISPATCH {event}] args: {args} kwargs: {kwargs}')


class Command(Generic[P, R]):
    """Represents a command.

    Attributes
    ----------
    name: str
        The name of this command.
    aliases: List[str]
        A list of aliases for this command.
    callback: Callable
        The callback for when this command is invoked.
    error_callback: Optional[Callable[[:class:`~.Context`, Exception], Any]]
        The callback for when an error is raise during command invokation.
        This could be ``None``.
    """

    def __init__(
        self,
        callback: CommandCallback,
        *,
        name: str,
        aliases: Sequence[str],
        brief: Optional[str] = None,
        description: Optional[str] = None,
        **attrs
    ) -> None:
        self.callback: CommandCallback = callback
        self.error_callback: Optional[ErrorCallback] = None

        self.name: str = name
        self.aliases: List[str] = list(aliases)

        self._brief: Optional[str] = brief
        self._description: Optional[str] = description

        self._metadata: Dict[str, Any] = attrs

    def error(self, func: ErrorCallback) -> None:
        """Registers an error handler for this command.
        If no errors are raised here, the error is suppressed.
        Else, `on_command_error` is raised.

        Function signature should be of ``async (ctx: Context, error: Exception) -> Any``.
        """
        self.error_callback = func

    async def invoke(self, ctx: Context, /, *args: P.args, **kwargs: P.kwargs) -> None:
        """|coro|

        Invokes this command with the given context.

        Parameters
        ----------
        ctx: :class:`~.Context`
            The context to invoke this command with.
        *args
            The positional arguments to pass into the callback.
        **kwargs
            The keyword arguments to pass into the callback.
        """
        # Replace `_temporary_dispatch` with an event dispatcher of your choice.
        try:
            _temporary_dispatch('command', ctx)
            await self.callback(ctx, *args, **kwargs)
        except Exception as exc:
            if self.error_callback:
                try:
                    await self.error_callback(ctx, exc)
                except Exception as new_exc:
                    exc = new_exc
                else:
                    return

            _temporary_dispatch('command_error', ctx, exc)
        else:
            _temporary_dispatch('command_success', ctx)
        finally:
            _temporary_dispatch('command_complete', ctx)


class Context:
    """Represents the context for when a command is invoked.

    Attributes
    ----------
    command: :class:`~.Command`
        The command invoked. Could be ``None``.
    args: tuple
        The arguments used to invoke this command. Could be ``None``.
    kwargs: Dict[str, Any]
        The keyword arguments used to invoke this command. Could be ``None``.
    """

    def __init__(self) -> None:
        self.command: Optional[Command] = None
        self.args: Optional[Tuple[P.args, ...]] = None
        self.kwargs: Optional[Dict[str, P.kwargs]] = None

    async def invoke(self, command: Command[P, Any], /, *args: P.args, **kwargs: P.kwargs) -> None:
        """|coro|

        Invokes the given command with this context.

        .. note:: No checks will be called here.

        Parameters
        ----------
        command: :class:`~.Command`
            The context to invoke this command with.
        *args
            The positional arguments to pass into the callback.
        **kwargs
            The keyword arguments to pass into the callback.
        """
        self.command = command
        self.args = args
        self.kwargs = kwargs

        await command.invoke(self, *args, **kwargs)

    async def reinvoke(self) -> None:
        """|coro|

        Re-invokes this command with the same arguments.

        .. note:: No checks will be called here.
        """
        await self.invoke(self.command, *self.args, **self.kwargs)
