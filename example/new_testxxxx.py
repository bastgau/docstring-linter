"""Short module description on the first line.

Detailed module description if needed. Can span multiple lines
with consistent indentation.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator


class NewTest:
    """Display class description on the first line."""

    def __init__(self) -> None:
        """Short method description on the first line."""
        print("eee")  # noqa: T201

    def totoxxx(self) -> None:
        """Short method description on the first line.

        Returns:
            None

        """
        print("eee")  # noqa: T201

class NewTes2:
    """Display class description on the first line."""

    def __init__(self) -> None:
        """Short method description on the first line."""

    def totoxxx(self, xxx: int) -> None:
        """Ceci est un sumary.

        Ceci est la suite
        ou une description.

        Args:
            xxx (int): xxxx

        Returns:
            None

        Raises:
            RuntimeError: xxx

        """
        del xxx

        msg = "xxxxxx"
        raise RuntimeError(msg)

def cfg(value: str, **kwargs: str) -> str:
    """Copy the default config and override the given attributes.

    Args:
        value (str): xxxx
        **kwargs (str): xxx

    Returns:
        str: xxx

    Raises:
        RuntimeError: xxx

    """
    del kwargs
    raise RuntimeError
    return value

def read_lines(path: str) -> Iterator[str]:
    """Read lines from a file one by one.

    Args:
        path (str): xxx

    Yields:
        str: xxx

    """
    with open(path, encoding="utf8") as f:  # noqa: PTH123
        for line in f:
            yield line.strip()


def totoxxx() -> None:
    print("eee")  # noqa: T201
