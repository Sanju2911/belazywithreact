import re
import shutil
import subprocess
from pathlib import Path

_PROJECT_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_WINDOWS_RESERVED = {"con", "prn", "aux", "nul", "conin$", "conout$"} | {
    f"{prefix}{number}" for prefix in ("com", "lpt") for number in range(1, 10)
}


def validate_project_name(name: str) -> str:
    if not name or name in {".", ".."}:
        raise ValueError("Project name must be a non-empty directory name.")
    if not _PROJECT_NAME.fullmatch(name):
        raise ValueError(
            "Project name may contain only letters, numbers, dots, underscores, and hyphens, "
            "and must start with a letter or number."
        )
    if name.endswith(".") or name.endswith(" "):
        raise ValueError("Project name cannot end with a dot or space.")
    if name.split(".", 1)[0].lower() in _WINDOWS_RESERVED:
        raise ValueError("Project name is reserved on Windows. Choose another name.")
    if len(name) > 214 or name.lower() in {"node_modules", "favicon.ico"}:
        raise ValueError("Project name is reserved by npm or exceeds 214 characters.")
    return name


def resolve_destination(name: str, cwd: Path | None = None) -> Path:
    validate_project_name(name)
    base = (cwd or Path.cwd()).resolve()
    destination = (base / name).resolve()
    if destination == base or base not in destination.parents:
        raise ValueError("Destination must be a child directory of the current directory.")
    if (base / name).is_symlink():
        raise ValueError("Destination is a symbolic link. Choose another project name.")
    return destination


def check_node_tools() -> tuple[str, str]:
    node = shutil.which("node")
    npm = shutil.which("npm.cmd") or shutil.which("npm")
    missing = []
    if not node:
        missing.append("Node.js (node)")
    if not npm:
        missing.append("npm")
    if missing:
        raise RuntimeError(
            "Missing required tool(s): " + ", ".join(missing) +
            ". Install a supported Node.js LTS release, then reopen your terminal."
        )
    try:
        result = subprocess.run([node, "--version"], check=True, capture_output=True, text=True, timeout=10)
        version = tuple(int(part) for part in result.stdout.strip().lstrip("v").split("."))
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        raise RuntimeError("Cannot run Node.js. Check the installation and PATH, then reopen your terminal.") from exc
    if version < (22, 13, 0) or version[0] % 2:
        raise RuntimeError("Use Node.js 22.13+ on an even-numbered release; Node.js 24 LTS is recommended.")
    return node, npm
