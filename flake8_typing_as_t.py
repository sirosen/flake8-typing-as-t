from __future__ import annotations

import argparse
import ast
import dataclasses
import importlib.metadata
import typing as t

import flake8

__version__ = importlib.metadata.version("flake8-typing-as-t")

_TYT00 = (
    "TYT00 {plugin_name} plugin misconfigured: expected the configured "
    "imported name to be a valid Python identifier but got {imported_name!r}"
)
_TYT01 = "TYT01 bare import of typing module"
_TYT02 = "TYT02 import of typing module with an alias other than '{imported_name}'"
_TYT03 = "TYT03 import from typing module"
_TYT80 = (
    "TYT80 use of a deprecated typing module member superseded by builtins: '{name}'"
)
_TYT81 = "TYT81 use of a deprecated typing module member with planned removal: '{name}'"


@dataclasses.dataclass
class Plugin:
    name = "typing-as-t"
    version = __version__
    tree: ast.AST
    _imported_name: t.ClassVar[str]

    def run(self):
        imported_name = self._imported_name
        if not imported_name.isidentifier():
            yield (
                0,
                0,
                _TYT00.format(
                    plugin_name=self.name,
                    imported_name=imported_name,
                ),
                None,
            )
            return

        visitor = TYTVisitor(imported_name=imported_name)
        visitor.visit(self.tree)
        for node, message in visitor.collect:
            yield node.lineno, node.col_offset, message, None

    @classmethod
    def add_options(
        cls,
        option_manager: flake8.options.manager.OptionManager,
        /,
    ) -> None:
        """Register plugin configuration options.

        :param option_manager: flake8's variant of the option parser object
        """
        option_manager.add_option(
            f"--{cls.name}-imported-name",
            default="t",
            help=(
                "Name under which the `typing` module must be imported. "
                "(Default: %(default)s)"
            ),
            metavar="imported_name",
            parse_from_config=True,
            type=str,
        )

    @classmethod
    def parse_options(
        cls,
        option_manager: flake8.options.manager.OptionManager,
        options: argparse.Namespace,
        args: list[str],  # options.filenames
        /,
    ) -> None:
        """Store user-provided configuration on the plugin class.

        :param option_manager: flake8's variant of the option parser object
        :param options: argparse namespace object
        :param args: a list of trailing CLI arguments interpreted as filenames
        """
        cls._imported_name = options.typing_as_t_imported_name


class TYTVisitor(ast.NodeVisitor):
    def __init__(self, *, imported_name) -> None:
        super().__init__()
        self._imported_name = imported_name
        self.collect = []
        self.in_version_check = False

        self._names_replaced_with_builtins: frozenset[str] = frozenset(
            (
                "Dict",
                "List",
                "Set",
                "FrozenSet",
                "Tuple",
                "Type",
            )
        )
        self._names_with_planned_removal: frozenset[str] = frozenset(
            (
                "ByteString",
                "no_type_check_decorator",
                "AnyStr",
            )
        )
        self._attrs_to_check = (
            self._names_replaced_with_builtins | self._names_with_planned_removal
        )

    def visit_If(self, node):
        oldval = self.in_version_check
        if _is_version_check(node):
            self.in_version_check = True
        self.generic_visit(node)
        self.in_version_check = oldval

    def visit_Import(self, node):  # an `import foo` clause
        for alias in node.names:
            if alias.name == "typing":
                if alias.asname is None:
                    self.collect.append((node, _TYT01))
                elif alias.asname != self._imported_name:
                    self.collect.append(
                        (
                            node,
                            _TYT02.format(imported_name=self._imported_name),
                        ),
                    )

    def visit_ImportFrom(self, node):  # an `from foo import ...` clause
        if node.module == "typing":
            if not self.in_version_check:
                self.collect.append((node, _TYT03))

    def visit_Attribute(self, node):  # any name node
        if (
            node.attr not in self._attrs_to_check
            or not isinstance(node.value, ast.Name)
            or node.value.id != self._imported_name
        ):
            return
        if node.attr in self._names_replaced_with_builtins:
            message = _TYT80.format(name=node.attr)
        else:
            message = _TYT81.format(name=node.attr)
        self.collect.append((node, message))


def _is_version_check(node: ast.If) -> bool:
    test = node.test
    if not isinstance(test, ast.Compare):
        return False

    all_values = [test.left] + test.comparators
    if len(all_values) == 2:
        left, right = all_values
        if isinstance(left, ast.Tuple):
            could_be_version = right
        elif isinstance(right, ast.Tuple):
            could_be_version = left
        else:
            return False
    elif len(all_values) == 3:
        could_be_version = all_values[1]
    else:
        return False

    if isinstance(could_be_version, ast.Name):
        if could_be_version.id == "version_info":
            return True
    elif isinstance(could_be_version, ast.Attribute):
        if could_be_version.attr == "version_info":
            name = could_be_version.value
            if isinstance(name, ast.Name) and name.id == "sys":
                return True
    else:
        return False
