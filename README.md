# flake8-typing-as-t

[![PyPI - Version](https://img.shields.io/pypi/v/flake8-typing-as-t.svg)](https://pypi.org/project/flake8-typing-as-t)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/flake8-typing-as-t.svg)](https://pypi.org/project/flake8-typing-as-t)

-----

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

## License

`flake8-typing-as-t` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Changelog

### 1.0.0

* Initial production release

### 0.0.3

* Internal refactoring for improved performance

### 0.0.2

* Add support for `sys.version_info` dispatch

### 0.0.1

* Initial release
