"""
Directly test the ImportVisitor and make sure it finds the right stuff.
"""

from flake8_typing_as_t import _TYT03, ImportVisitor


def test_finds_fromimport(parse_ast):
    tree = parse_ast(
        """\
        from typing import TypeVar
        """
    )
    visitor = ImportVisitor(imported_name="t")

    assert len(visitor.collect) == 0
    visitor.generic_visit(tree)
    assert len(visitor.collect) == 1
    finding = visitor.collect[0]
    assert finding[1] == _TYT03
