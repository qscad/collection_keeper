"""File with common jobs definitions. Run them with 'pdm run nox -e [job_name]'."""
import os
import tempfile

import nox
from nox.sessions import Session

os.environ.update(PDM_IGNORE_SAVED_PYTHON="1", PDM_USE_VENV="1")

PYSRC = ["src/", "noxfile.py", "tests/"]


@nox.session
def test(session: Session) -> None:
    """Run tests.

    Args:
        session (Session): nox session object
    """
    session.run_always("pdm", "install", "-G", "ci-tests", external=True)
    session.run("pytest", "--cov=src/", "tests/")


@nox.session
def format(session: Session) -> None:
    """Run autoformatters.

    Args:
        session (Session): nox session object
    """
    session.run_always("pdm", "install", "-G", "ci-quality", external=True)
    session.run("ssort", *PYSRC)
    session.run("isort", *PYSRC)
    session.run("ruff", "check", "--config", "config/ruff.toml", "--fix", *PYSRC)
    session.run("black", "--config", "config/black.toml", *PYSRC)


@nox.session
def lint(session: Session) -> None:
    """Run ruff checks.

    Args:
        session (Session): nox session object
    """
    session.run_always("pdm", "install", "-G", "ci-quality", external=True)
    session.run("ruff", "check", "--config", "config/ruff.toml", *PYSRC)


@nox.session
def check_types(session: Session) -> None:
    """Run type checking.

    Args:
        session (Session): nox session object
    """
    session.run_always("pdm", "install", "-G", "ci-quality", external=True)
    session.run("mypy", "--config-file", "config/mypy.ini", *PYSRC)


@nox.session
def check_safety(session: Session) -> None:
    """Run safety checks.

    Args:
        session (Session): nox session object
    """
    session.run_always("pdm", "install", "-G", "ci-quality", external=True)
    session.run("bandit", "-r", "--configfile", "config/bandit.toml", *PYSRC)
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "pdm",
            "export",
            "-f",
            "requirements",
            "-o",
            requirements.name,
            "--without-hashes",
            external=True,
        )
        session.run("safety", "check", f"--file={requirements.name}", "--full-report")


@nox.session
def generate_changelog(session: Session) -> None:
    """Generate changelog from the commits. It should be reviewed and cleaned up by a human.

    Args:
        session (Session): nox session object
    """
    session.run("git-changelog", "-Tbio", "CHANGELOG.md", "-c", "angular")
