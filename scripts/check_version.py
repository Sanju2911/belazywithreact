"""Reject inconsistent versions and release tags before publishing."""
import ast
import os
from pathlib import Path
import tomllib

root = Path(__file__).resolve().parents[1]
version = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
tree = ast.parse((root / "src/belazywithreact/__init__.py").read_text(encoding="utf-8"))
module_version = next(ast.literal_eval(node.value) for node in tree.body
                      if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "__version__" for target in node.targets))
if version != module_version:
    raise SystemExit("pyproject.toml and __version__ must match")
tag = os.environ.get("RELEASE_TAG")
if tag and tag != f"v{version}":
    raise SystemExit(f"Release tag must be v{version}; received {tag!r}")
print(f"Version validated: {version}")
