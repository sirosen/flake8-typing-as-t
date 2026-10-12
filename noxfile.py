import sys

import nox

nox.options.reuse_existing_virtualenvs = True
nox.options.default_venv_backend = "uv|virtualenv"

PYPROJECT = nox.project.load_toml("pyproject.toml")
PYTHONS = nox.project.python_versions(PYPROJECT, max_version="3.15")
MAX_PYTHON = max(PYTHONS)  # lexical sort applied via 'max' works
MIN_PYTHON = min(PYTHONS)


def _is_parallel(session: nox.Session) -> bool:
    # in future versions of nox, use `session.parallel`
    return "--parallel" in sys.argv


@nox.session(python=MAX_PYTHON, default=False, tags=["verify"])
def demo(session: nox.Session) -> None:
    """Run on the demo files; expect failure."""
    session.install("flake8", "-e.")
    session.run(
        "flake8",
        "--config",
        "demo-files/flake8-config.ini",
        "demo-files/",
        success_codes=(1,),
    )


@nox.session(python=MAX_PYTHON, default=False, tags=["lint", "verify"])
def prek(session: nox.Session) -> None:
    """Run linters and fixers."""
    session.install("prek")
    session.run("prek", "run", "--all-files", *session.posargs)


@nox.session(default=False, tags=["lint", "verify"])
def checkdists(session: nox.Session) -> None:
    """Check distribution data."""
    session.install("check-sdist")
    session.run("check-sdist", "--inject-junk", *session.posargs)


@nox.session(
    python=PYTHONS, requires=["covclean"], allow_parallel=True, tags=["verify"]
)
def test(session: nox.Session) -> None:
    """Run tests."""
    session.install(*nox.project.dependency_groups(PYPROJECT, "test"))
    session.install("-e.")
    env = {}
    if _is_parallel(session):
        env.update({"PYTEST_XDIST_AUTO_NUM_WORKERS": "0"})
    session.run("coverage", "run", "-m", "pytest", "-v", *session.posargs, env=env)


@nox.session(python=MAX_PYTHON)
def covclean(session: nox.Session) -> None:
    """Clean up coverage data."""
    session.install("coverage")
    session.run("coverage", "erase", *session.posargs)


@nox.session(python=MAX_PYTHON, requires=["test"])
def covcombine(session: nox.Session) -> None:
    """Combine coverage data."""
    session.install("coverage")
    session.run("coverage", "combine", *session.posargs)


@nox.session(python=MAX_PYTHON, requires=["covcombine"], tags=["verify"])
def covreport(session: nox.Session) -> None:
    """Create coverage HTML and text reports."""
    session.install("coverage")
    session.run("coverage", "html", "--fail-under=0", *session.posargs)
    session.run("coverage", "report", *session.posargs)
