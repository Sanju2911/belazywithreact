import subprocess

import pytest
from typer.testing import CliRunner

from belazywithreact import cli

runner = CliRunner()


@pytest.mark.parametrize("args", [["--help"], ["create", "--help"]])
def test_help(args):
    result = runner.invoke(cli.app, args)
    assert result.exit_code == 0
    assert "create" in result.output.lower()


@pytest.mark.parametrize("args", [["create"], ["create", "../bad", "--yes"],
    ["create", "demo", "--styling", "bad"], ["create", "demo", "--package-manager", "yarn"]])
def test_invalid_arguments(args):
    assert runner.invoke(cli.app, args).exit_code == 2


def test_existing_destination(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "demo").mkdir()
    result = runner.invoke(cli.app, ["create", "demo", "--yes"])
    assert result.exit_code == 2
    assert "already exists" in result.output


def test_missing_tools(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli, "check_node_tools", lambda: (_ for _ in ()).throw(RuntimeError("Install Node.js")))
    result = runner.invoke(cli.app, ["create", "demo", "--yes"])
    assert result.exit_code == 2
    assert "Install Node.js" in result.output


@pytest.mark.parametrize("failure,code,message", [
    (subprocess.CalledProcessError(7, ["npm", "install"]), 1, "Setup failed"),
    (KeyboardInterrupt(), 130, "interrupted"),
    (FileExistsError("Destination already exists"), 2, "already exists"),
])
def test_failure_exit_codes(tmp_path, monkeypatch, failure, code, message):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli, "check_node_tools", lambda: ("node", "npm"))
    def fail(*args):
        raise failure
    monkeypatch.setattr(cli, "create_project", fail)
    result = runner.invoke(cli.app, ["create", "demo", "--yes"])
    assert result.exit_code == code
    assert message in result.output


def test_cancel_does_not_create(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli, "check_node_tools", lambda: ("node", "npm"))
    monkeypatch.setattr(cli, "create_project", lambda *args: pytest.fail("must not create"))
    result = runner.invoke(cli.app, ["create", "demo"], input="n\n")
    assert result.exit_code == 0
    assert "Cancelled" in result.output


def test_defaults_and_options(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli, "check_node_tools", lambda: ("node", "npm"))
    calls = []
    monkeypatch.setattr(cli, "create_project", lambda *args: calls.append(args))
    result = runner.invoke(cli.app, ["create", "demo", "--yes"])
    assert result.exit_code == 0
    assert calls[0][2].router and calls[0][2].vitest
    assert calls[0][2].styling == "both"
    result = runner.invoke(cli.app, ["create", "other", "--yes", "--no-router", "--no-vitest"])
    assert result.exit_code == 0
    assert not calls[1][2].router and not calls[1][2].vitest
