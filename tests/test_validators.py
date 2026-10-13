from pathlib import Path

import pytest

import subprocess

from belazywithreact import validators
from belazywithreact.validators import check_node_tools, resolve_destination, validate_project_name


@pytest.mark.parametrize("name", ["my-app", "My_App", "app123", "app.test"])
def test_valid_project_names(name):
    assert validate_project_name(name) == name


@pytest.mark.parametrize("name", ["", ".", "..", "../oops", "my app", "a/b", "x;rm", "a.",
    "CON", "con.txt", "LPT1", "com9.log", "node_modules", "favicon.ico", "x" * 215, "x%PATH%", "x&dir"])
def test_invalid_project_names(name):
    with pytest.raises(ValueError):
        validate_project_name(name)


def test_resolve_destination_is_child(tmp_path: Path):
    result = resolve_destination("demo", tmp_path)
    assert result == (tmp_path / "demo").resolve()
    assert tmp_path.resolve() in result.parents


@pytest.mark.parametrize("version", ["v22.13.0", "v24.14.1", "v26.0.0"])
def test_supported_node(monkeypatch, version):
    monkeypatch.setattr(validators.shutil, "which", lambda name: name)
    monkeypatch.setattr(validators.subprocess, "run", lambda *a, **kw: subprocess.CompletedProcess(a, 0, version))
    assert check_node_tools() == ("node", "npm.cmd")


@pytest.mark.parametrize("version", ["v20.19.0", "v22.12.0", "v23.0.0", "invalid"])
def test_unsupported_node(monkeypatch, version):
    monkeypatch.setattr(validators.shutil, "which", lambda name: name)
    monkeypatch.setattr(validators.subprocess, "run", lambda *a, **kw: subprocess.CompletedProcess(a, 0, version))
    with pytest.raises(RuntimeError):
        check_node_tools()


@pytest.mark.parametrize("missing", ["node", "npm", "both"])
def test_missing_tools(monkeypatch, missing):
    monkeypatch.setattr(validators.shutil, "which", lambda name: None if missing == "both" or name.startswith(missing) else name)
    with pytest.raises(RuntimeError, match="Install"):
        check_node_tools()


def test_broken_node(monkeypatch):
    monkeypatch.setattr(validators.shutil, "which", lambda name: name)
    def fail(*a, **kw):
        raise OSError("broken")
    monkeypatch.setattr(validators.subprocess, "run", fail)
    with pytest.raises(RuntimeError, match="Cannot run Node"):
        check_node_tools()
