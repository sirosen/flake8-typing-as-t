import ast

__version__ = "0.0.1"

_CODEMAP = {
    "TYI01": "bare import of typing module",
    "TYI02": "import of typing module with an alias other than 't'",
    "TYI03": "import from typing module",
}


class Plugin:
    name = "typing-imports"
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


class ImportVisitor(ErrorRecordingVisitor):
    def visit_Import(self, node):  # an `import foo` clause
        for alias in node.names:
            if alias.name == "typing":
                if alias.asname is None:
                    self._record(node, "TYI01")
                elif alias.asname != "t":
                    self._record(node, "TYI02")

    def visit_ImportFrom(self, node):  # an `from foo import ...` clause
        if node.module == "typing":
            self._record(node, "TYI03")
