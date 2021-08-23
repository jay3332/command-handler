from __future__ import annotations

from typing import (
    Awaitable,
    Callable,
    Dict,
    Generator,
    Optional,
    TYPE_CHECKING,
    TypeVar,
    Sequence,
    Union,
)

from .models import Command

if TYPE_CHECKING:
    _BasePrefixT = Union[str, Sequence[str]]
    PrefixT = Union[_BasePrefixT, Callable[['Bot', Message], Union[_BasePrefixT, Awaitable[_BasePrefixT]]]]
    DefaultT = TypeVar('DefaultT')


class CaseInsensitiveDict(Dict[K, V]):
    """Represents a case-insensitive dictionary."""

    def __getitem__(self, key: K) -> V:
        return super().__getitem__(key.casefold())

    def __setitem__(self, key: K, value: V) -> None:
        super().__setitem__(key.casefold(), v)

    def __delitem__(self, key: K) -> None:
        return super().__delitem__(key.casefold())

    def __contains__(self, key: K) -> bool:
        return super().__contains__(key.casefold())

    def get(self, key: K, default: Any = None) -> Optional[V]:
        return super().get(key.casefold(), default)

    def pop(self, key: K, default: Any = None) -> V:
        return super().pop(key.casefold(), default)

    get.__doc__ = dict.get.__doc__
    pop.__doc__ = dict.pop.__doc__


class CommandSink:
    """Represents a sink of commands.
    This will both mixin to :class:`~.Bot` and :class:`~.CommandGroup`.

    Attributes
    ----------
    mapping: Dict[str, :class:`.Command`]
        A full mapping of command names to commands.
    """

    def __init__(self, *, case_insensitive: bool = False) -> None:
        mapping_factory = CaseInsensitiveDict if case_insensitive else dict
        self.mapping: Dict[str, Command] = mapping_factory()

    def walk_commands(self) -> Generator[Command]:
        """Returns a generator that walks through all of the commands
        this sink holds.

        Returns
        -------
        Generator[:class:`.Command`]
        """
        seen = set()
        for command in self.mapping.values():
            if command not in seen:
                seen.add(command)
                yield command

    def get_command(self, name: str, /, default: Any = None) -> Optional[Command]:
        """Tries to get a command by it's name.
        Aliases are supported.

        Parameters
        ----------
        name: str
            The name of the command you want to lookup.
        default
            What to return instead if the command was not found.
            Defaults to ``None``.

        Returns
        -------
        Optional[:class:`~.Command`]
            The command found.
        """
        return self.mapping.get(name, default)

    @property
    def commands(self) -> None:
        """List[:class:`.Command`]: A list of the commands this sink holds."""
        return list(self.walk_commands())


class Bot(CommandSink):
    """Represents a bot with extra command handling support.

    Parameters
    ----------
    prefix
        The prefix this bot will listen for. This is required.
    case_insensitive: bool
        Whether or not commands should be case-insensitive.
    """

    def __init__(self, prefix: PrefixT, *, case_insensitive: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        CommandSink.__init__(self, case_insensitive=case_insensitive)

        self.prefix: PrefixT = prefix
        self._default_case_insensitive: bool = case_insensitive
