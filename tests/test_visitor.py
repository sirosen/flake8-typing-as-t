"""
Directly test the ImportVisitor and make sure it finds the right stuff.
"""

import pytest

from flake8_typing_as_t import _TYT03, _TYT80, _TYT81, TYTVisitor


def test_finds_fromimport(parse_ast):
    tree = parse_ast(
        """\
        from typing import TypeVar
        """
    )
    visitor = TYTVisitor(imported_name="t")

    assert len(visitor.collect) == 0
    visitor.generic_visit(tree)
    assert len(visitor.collect) == 1
    finding = visitor.collect[0]
    assert finding[1] == _TYT03


@pytest.mark.parametrize(
    "deprecated_name",
    ("Dict", "List", "Set", "FrozenSet", "Tuple", "Type"),
)
@pytest.mark.parametrize("typing_name", ("typ", "t", "_t"))
def test_finds_deprecated_name_replaced_with_builtin(
    parse_ast, deprecated_name, typing_name
):
    tree = parse_ast(
        f"""\
        import typing as {typing_name}

        x = {typing_name}.{deprecated_name}
        """
    )
    visitor = TYTVisitor(imported_name=typing_name)

    assert len(visitor.collect) == 0
    visitor.generic_visit(tree)
    assert len(visitor.collect) == 1
    finding = visitor.collect[0]
    assert finding[1] == _TYT80.format(name=deprecated_name)


@pytest.mark.parametrize(
    "deprecated_name",
    ("ByteString", "no_type_check_decorator", "AnyStr"),
)
@pytest.mark.parametrize("typing_name", ("typ", "t", "_t"))
def test_finds_deprecated_name_with_planned_removal(
    parse_ast, deprecated_name, typing_name
):
    tree = parse_ast(
        f"""\
        import typing as {typing_name}

        x = {typing_name}.{deprecated_name}
        """
    )
    visitor = TYTVisitor(imported_name=typing_name)

    assert len(visitor.collect) == 0
    visitor.generic_visit(tree)
    assert len(visitor.collect) == 1
    finding = visitor.collect[0]
    assert finding[1] == _TYT81.format(name=deprecated_name)
