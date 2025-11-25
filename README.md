# flake8-typing-as-t

**Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [License](#license)

## Overview

This is a `flake8` plugin which ensures that imports from the `typing` library must be written using `import typing as t`.

## Installation

```console
pip install flake8-typing-as-t
```

## Checks

- `TYT01`: Bare `import typing` usage
- `TYT02`: `import typing as X` where `X` is not literal `t`
- `TYT03`: `from typing import X` usage

## Handling `typing-extensions`

A common pattern for compatibility is to do a `sys.version_info`-guarded
dispatch over `typing_extensions`. e.g.

```python
if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal
```

`flake8-typing-as-t` allows for this usage by checking if the import is inside
of a test on `sys.version_info` against a tuple.

## Configuring the Import Name

By default, `flake8-typing-as-t` enforces that the style be `import typing as t`.
However, another common style, with the same benefits, is `import typing as _t`.

`import typing as _t` can be helpful in projects with strong policies around private vs public module members (including imported names).

To support this style, and other potential conventions, `flake8-typing-as-t` supports a config and CLI flag:

```bash
flake8 --typing-as-t-import-name "_t"
```

or, in `.flake8` config:

```ini
[flake8]
typing-as-t-import-name = _t
```

## Inspiration and Rationale

I first saw `import typing as t` in the `pallets` projects, probably in `flask` or `click`.

It didn't _click_ for me right away!
But after working on various codebases with different strategies (including no
strategy) for how to handling `typing` imports, the benefits became clear.

There are three primary consistent ways of handling `typing` imports:

- always `from typing import <Symbol>`
- always `import typing`
- always `import typing as t`

Examining the problems with the other styles shows that `import typing as t`
is the best choice.

The trouble with standardizing around the from-import style is that your import
lines are constantly changing as code evolves.
```diff
+from typing import Any, ClassVar
-from typing import Any
```

Which means that as a reviewer, you are exposed to a lot more churn, and (much
worse!) you frequently deal with "dumb" merge conflicts when two PRs change the
same import lines.

`import typing` solves the conflict/diff problem, but frequently makes otherwise
short function signature lines and other usages wrap.

Consider:

```python
def foo(xs: typing.Iterator[T | None], ys: typing.Iterator[T | None]) -> typing.Iterator[tuple[T, T]]:
    for item1, item2 in zip(xs, ys):
        if item1 is not None and item2 is not None:
            yield (item1, item2)
```

vs

```python
def foo(xs: t.Iterator[T | None], ys: t.Iterator[T | None]) -> t.Iterator[tuple[T, T]]:
    ...
```

That's a 102 character signature vs an 87 character one.
A max line length of 88 chars is common.
Surprisingly often, the extra characters in `typing` are the only reason that a
line will wrap under code style rules.

### A Neighbor of Builtins

Treating the `typing` module specially in your code, enforcing that it's always
imported under a special single character name, also has a strong influence on
how you think about `typing` in Python.

`t` becomes a special symbol for "parts of the type system".
`typing` becomes more similar to the language level builtins, without the
namespace pollution and readability problems we'd have with a star-import.

## License

`flake8-typing-as-t` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Changelog

### 1.1.0

* Added support for configuring the import name, for `as _t` style

### 1.0.0

* Initial production release

### 0.0.3

* Internal refactoring for improved performance

### 0.0.2

* Add support for `sys.version_info` dispatch

### 0.0.1

* Initial release
