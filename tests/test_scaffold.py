import json
import subprocess

import pytest

from belazywithreact import scaffold
from belazywithreact.scaffold import CREATE_VITE_VERSION, ProjectOptions, create_project, run_command


@pytest.fixture
def vite_runner(tmp_path, monkeypatch):
    # Test orchestration with argv; test the Windows launcher separately.
    monkeypatch.setattr(scaffold, "_IS_WINDOWS", False)
    destination = tmp_path / "demo"
    calls = []

    def fake_run(command, *, cwd=None, check=False):
        calls.append((command, cwd, check))
        if command[1] == "create":
            destination.mkdir()
            (destination / "src").mkdir()
            (destination / "package.json").write_text(json.dumps({
                "name": "demo", "scripts": {"dev": "vite", "build": "tsc -b && vite build", "lint": "eslint ."},
                "devDependencies": {"eslint": "10", "@eslint/js": "10", "typescript": "6"},
            }), encoding="utf-8")
            (destination / "eslint.config.js").write_text("export default []", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0)

    return destination, calls, fake_run


@pytest.mark.parametrize("is_file", [False, True])
def test_existing_destination_is_not_overwritten(tmp_path, is_file):
    destination = tmp_path / "demo"
    if is_file:
        destination.write_text("keep", encoding="utf-8")
        important = destination
    else:
        destination.mkdir()
        important = destination / "important.txt"
        important.write_text("keep", encoding="utf-8")
    with pytest.raises(FileExistsError):
        create_project("demo", destination, ProjectOptions())
    assert important.read_text(encoding="utf-8") == "keep"


@pytest.mark.parametrize("options", [ProjectOptions(package_manager="pnpm"), ProjectOptions(styling="invalid")])
def test_rejects_unsupported_options(tmp_path, options):
    with pytest.raises(ValueError):
        create_project("demo", tmp_path / "demo", options)
    assert not (tmp_path / "demo").exists()


@pytest.mark.parametrize("name", ["../oops", "bad&command", "different", "CON"])
def test_library_validates_name_before_running(tmp_path, name):
    with pytest.raises(ValueError):
        create_project(name, tmp_path / "demo", ProjectOptions(), runner=lambda *a, **kw: pytest.fail("must not run"))


def test_default_starter(vite_runner):
    destination, calls, runner = vite_runner
    create_project("demo", destination, ProjectOptions(), runner=runner)
    assert calls[0][0] == ["npm", "create", f"vite@{CREATE_VITE_VERSION}", "demo", "--", "--template", "react-ts", "--no-interactive"]
    for relative in ("src/components/Button.tsx", "src/pages/HomePage.tsx", "src/styles/index.css",
                     "src/styles/tailwind.css", "src/App.tsx", "src/main.tsx", "src/services/api.ts",
                     "src/store/useAppStore.ts", "src/utils/example.test.ts", ".env.example",
                     "vite.config.ts", "eslint.config.js", ".prettierignore"):
        assert (destination / relative).is_file(), relative
    assert 'import "./index.css"' not in (destination / "src/main.tsx").read_text()
    assert "BrowserRouter" in (destination / "src/App.tsx").read_text()
    assert '@import "tailwindcss"' in (destination / "src/styles/tailwind.css").read_text()
    assert "tailwindcss()" in (destination / "vite.config.ts").read_text()
    assert "react-router-dom@7.18.4" in calls[1][0]
    assert "tailwindcss@4.3.3" in calls[2][0]
    assert "eslint@10.12.0" in calls[2][0]
    scripts = json.loads((destination / "package.json").read_text())["scripts"]
    assert scripts["test"] == "vitest run"
    assert scripts["test:watch"] == "vitest"
    assert scripts["format"] == "prettier --write ."
    assert scripts["lint"] == "eslint ."
    assert "!.env.example" in (destination / ".gitignore").read_text()
    assert calls[-1][0] == ["npm", "install"]


def test_minimal_project_installs_and_removes_eslint(vite_runner):
    destination, calls, runner = vite_runner
    options = ProjectOptions(styling="css", router=False, axios=False, zustand=False,
                             eslint=False, prettier=False, vitest=False)
    create_project("demo", destination, options, runner=runner)
    assert len(calls) == 2
    assert calls[-1][0] == ["npm", "install"]
    package = json.loads((destination / "package.json").read_text())
    assert "lint" not in package["scripts"]
    assert "test" not in package["scripts"]
    assert package["devDependencies"] == {"typescript": "6"}
    assert not (destination / "eslint.config.js").exists()
    assert not (destination / "tailwind.config.js").exists()
    assert not (destination / "src/services/api.ts").exists()
    assert not (destination / "src/store/useAppStore.ts").exists()
    assert "BrowserRouter" not in (destination / "src/App.tsx").read_text()
    assert "npm run lint" not in (destination / "README.md").read_text()


def test_vite_does_not_create_folder(tmp_path, monkeypatch):
    monkeypatch.setattr(scaffold, "_IS_WINDOWS", False)
    with pytest.raises(RuntimeError, match="expected directory"):
        create_project("demo", tmp_path / "demo", ProjectOptions(), runner=lambda *a, **kw: None)


def test_npm_failure_preserves_partial_project(vite_runner):
    destination, calls, runner = vite_runner
    def failing(command, **kwargs):
        if command[1] == "install":
            raise subprocess.CalledProcessError(42, command)
        return runner(command, **kwargs)
    with pytest.raises(subprocess.CalledProcessError):
        create_project("demo", destination, ProjectOptions(), runner=failing)
    assert (destination / "src/App.tsx").exists()


def test_windows_npm_cmd_quoting(tmp_path, monkeypatch):
    monkeypatch.setattr(scaffold, "_IS_WINDOWS", True)
    monkeypatch.setattr(scaffold.shutil, "which", lambda name: r"C:\Program Files\nodejs\npm.cmd")
    calls = []
    run_command(["npm", "--version"], cwd=tmp_path, runner=lambda *a, **kw: calls.append((a, kw)))
    assert calls == [((r'call "C:\Program Files\nodejs\npm.cmd" --version',),
                      {"cwd": str(tmp_path), "check": True, "shell": True})]


@pytest.mark.parametrize("argument", ["x&whoami", "x|whoami", "%PATH%", "a\nb", 'a"b', "a^b", "a!b", "a>b"])
def test_windows_rejects_shell_syntax(monkeypatch, argument):
    monkeypatch.setattr(scaffold, "_IS_WINDOWS", True)
    monkeypatch.setattr(scaffold.shutil, "which", lambda name: "npm.cmd")
    with pytest.raises(ValueError, match="Unsafe"):
        run_command(["npm", argument], runner=lambda *a, **kw: pytest.fail("must not run"))


def test_missing_windows_npm(monkeypatch):
    monkeypatch.setattr(scaffold, "_IS_WINDOWS", True)
    monkeypatch.setattr(scaffold.shutil, "which", lambda name: None)
    with pytest.raises(FileNotFoundError, match="Node.js"):
        run_command(["npm", "--version"])


def test_posix_uses_argv_without_shell(monkeypatch):
    monkeypatch.setattr(scaffold, "_IS_WINDOWS", False)
    calls = []
    run_command(["npm", "--version"], runner=lambda *a, **kw: calls.append((a, kw)))
    assert calls == [((["npm", "--version"],), {"cwd": None, "check": True})]
