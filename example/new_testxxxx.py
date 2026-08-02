"""Short module description on the first line.

Detailed module description if needed. Can span multiple lines
with consistent indentation.
"""

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
        str: Config carrying the default values plus the overrides.

    """
    del kwargs
    return value
