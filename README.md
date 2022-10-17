# flake8-typing-imports

[![PyPI - Version](https://img.shields.io/pypi/v/flake8-typing-imports.svg)](https://pypi.org/project/flake8-typing-imports)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/flake8-typing-imports.svg)](https://pypi.org/project/flake8-typing-imports)

-----

**Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [License](#license)

## Overview

This is a flake8 plugin which ensures that imports from the `typing` library must be written using `import typing as t`.

## Installation

```console
pip install flake8-typing-imports
```

## Checks

- `TYI01`: Bare `import typing` usage
- `TYI02`: `import typing as X` where `X` is not literal `t`
- `TYI03`: `from typing import X` usage

## Handling `typing-extensions`

A common pattern for compatibility is to do a `sys.version_info`-guarded
dispatch over `typing_extensions`. e.g.

```python
if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal
```

Currently, `flake8-typing-imports` does not have special handling for this.
Users should use a `noqa` comment as follows:

```python
if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal  # noqa: TYIMP03
```

## License

`flake8-typing-imports` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
