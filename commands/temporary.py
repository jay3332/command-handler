"""Temporary models/functions that should be replaced with lib-specific counterparts."""


class _TemporaryClient:
    """Replace this with the base client model of your library."""


class _TemporaryMessage:
    """Replace this with the message model of your library."""

    def __init__(self, content: str) -> None:
        self.content = content


def _temporary_dispatch(event: str, *args, **kwargs) -> None:
    """Replace this with the event dispatcher callback of your library."""
    print(f'[DISPATCH {event}] args: {args} kwargs: {kwargs}')


# For type-hinting
Message = _TemporaryMessage
