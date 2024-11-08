import ast
import dataclasses

__version__ = "1.0.0"

_TYT01 = "TYT01 bare import of typing module"
_TYT02 = "TYT02 import of typing module with an alias other than 't'"
_TYT03 = "TYT03 import from typing module"


@dataclasses.dataclass
class Plugin:
    name = "typing-as-t"
    version = __version__
    tree: ast.AST

    def run(self):
        visitor = ImportVisitor()
        visitor.visit(self.tree)
        for node, message in visitor.collect:
            yield node.lineno, node.col_offset, message, None


class ImportVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.collect = []
        self.in_version_check = False

    def visit_If(self, node):
        oldval = self.in_version_check
        if _is_version_check(node):
            self.in_version_check = True

        for child in ast.iter_child_nodes(node):
            self.visit(child)

        self.in_version_check = oldval

    def visit_Import(self, node):  # an `import foo` clause
        for alias in node.names:
            if alias.name == "typing":
                if alias.asname is None:
                    self.collect.append((node, _TYT01))
                elif alias.asname != "t":
                    self.collect.append((node, _TYT02))

    def visit_ImportFrom(self, node):  # an `from foo import ...` clause
        if node.module == "typing":
            if not self.in_version_check:
                self.collect.append((node, _TYT03))


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
