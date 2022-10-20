import ast

__version__ = "0.0.2"

_CODEMAP = {
    "TYT01": "bare import of typing module",
    "TYT02": "import of typing module with an alias other than 't'",
    "TYT03": "import from typing module",
}


class Plugin:
    name = "typing-as-t"
    version = __version__

    # args to init determine plugin behavior. see:
    # https://flake8.pycqa.org/en/latest/internal/utils.html#flake8.utils.parameters_for
    def __init__(self, tree):
        self.tree = tree

    # Plugin.run() is how checks will run. For detail, see implementation of:
    # https://flake8.pycqa.org/en/latest/internal/checker.html#flake8.checker.FileChecker.run_ast_checks
    def run(self):
        visitor = ImportVisitor()
        visitor.visit(self.tree)
        for lineno, col, code in visitor.collect:
            yield lineno, col, code + " " + _CODEMAP[code], type(self)


class ErrorRecordingVisitor(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.collect = []

    def _record(self, node, code):
        self.collect.append((node.lineno, node.col_offset, code))


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


class ImportVisitor(ErrorRecordingVisitor):
    def __init__(self):
        super().__init__()
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
                    self._record(node, "TYT01")
                elif alias.asname != "t":
                    self._record(node, "TYT02")

    def visit_ImportFrom(self, node):  # an `from foo import ...` clause
        if node.module == "typing":
            if not self.in_version_check:
                self._record(node, "TYT03")
