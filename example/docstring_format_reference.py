"""Short module description on the first line.

Detailed module description if needed. Can span multiple lines
with consistent indentation.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

class MyClass:
    """Short class description on the first line.

    Detailed class description if needed.

    Attributes:
        name (str): Description of the attribute.
        count (int): Description of the attribute.

    """

    def __init__(self, name: str, count: int = 0) -> None:
        """Short method description on the first line.

        Args:
            name (str): Description of the parameter.
            count (int): Description of the parameter. Defaults to 0.

        Returns:
            None: This method returns nothing.

        """
        self.name = name
        self.count = count

    def process(self, value: int, *, strict: bool = False) -> dict[str, int]:
        """Short method description on the first line.

        Detailed description if needed. Can span multiple lines
        with consistent indentation.

        Args:
            value (int): Description of the parameter.
            strict (bool): Description of the parameter. Defaults to False.

        Returns:
            dict[str, int]: Short description of what is returned.

        Raises:
            ValueError: When this exception is raised.

        Example:
            >>> obj = MyClass("test")
            >>> obj.process(42)
            {'result': 42}

        """
        if strict and value < 0:
            msg_must_be_positive = "value must be positive in strict mode"
            raise ValueError(msg_must_be_positive)
        return {"result": value}

    def reset(self) -> None:
        """Short one-liner for simple methods."""
        self.count = 0

def divide_new(numerator: int, *, denominator: int) -> float:
    """Divide two numbers.

    Args:
        numerator (int): The dividend.
        denominator (int): The divisor.

    Returns:
        float: The quotient.

    """
    return numerator / denominator


def divide(numerator: int, denominator: int, /) -> float:
    """Divide two numbers.

    Args:
        numerator (int): The dividend.
        denominator (int): The divisor.

    Returns:
        float: The quotient.

    """
    divide_new(4, denominator=7)

    return numerator / denominator

def my_function(data: list[object], limit: int = 10) -> list[object]:
    """Short function description on the first line.

    Args:
        data (list[object]): Description of the parameter.
        limit (int): Description of the parameter. Defaults to 10.

    Returns:
        list[object]: Short description of what is returned.

    Raises:
        ValueError: When this exception is raised.

    """

    def new_limit(x: int) -> int:
        if x > 100:  # noqa: PLR2004
            msg = "stop"
            raise RuntimeError(msg)
        return x

    limit = new_limit(limit)

    if not data:
        msg_cannot_be_empty = "Data cannot be empty"
        raise ValueError(msg_cannot_be_empty)
    return data[:limit]


def simple_function() -> None:
    """Short one-liner for simple functions."""


def read_lines(path: str) -> Iterator[str]:
    """Read lines from a file one by one.

    Args:
        path (str): Path to the file.

    Yields:
        str: Each line of the file stripped of whitespace.

    """
    with open(path, encoding="utf8") as f:  # noqa: PTH123
        for line in f:
            yield line.strip()
