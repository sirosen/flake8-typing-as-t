import ast
import textwrap

import pytest


@pytest.fixture
def parse_ast():
    def func(data):
        dedented = textwrap.dedent(data)
        return ast.parse(dedented)

    return func
