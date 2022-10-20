import sys
import typing as t

if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal


def foo(x: Literal["a", "b"] = "a") -> t.Any:
    return x
