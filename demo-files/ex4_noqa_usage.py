import sys
import typing as t

if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal  # noqa: TYT03


def foo(x: Literal["a", "b"] = "a") -> t.Any:
    return x
