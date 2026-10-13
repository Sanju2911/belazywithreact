"""Validate the exact upload set, metadata, and archive contents (Python 3.10+)."""
from email.parser import BytesParser
from pathlib import Path, PurePosixPath
import tarfile
import zipfile

dist = Path("dist")
files = sorted(dist.iterdir())
wheels = [path for path in files if path.name.startswith("belazywithreact-") and path.suffix == ".whl"]
sdists = [path for path in files if path.name.startswith("belazywithreact-") and path.name.endswith(".tar.gz")]
if len(files) != 2 or len(wheels) != 1 or len(sdists) != 1:
    raise SystemExit("dist must contain exactly one belazywithreact wheel and one sdist")
versions = set()
for path in files:
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            metadata = next(name for name in names if name.endswith("/METADATA"))
            info = BytesParser().parsebytes(archive.read(metadata))
            if "belazywithreact/cli.py" not in names or "belazywithreact/scaffold.py" not in names:
                raise SystemExit("Wheel missing CLI source")
    else:
        with tarfile.open(path) as archive:
            names = archive.getnames()
            metadata = next(name for name in names if name.endswith("/PKG-INFO"))
            info = BytesParser().parsebytes(archive.extractfile(metadata).read())
    if info["Name"] != "belazywithreact" or info["License-Expression"] != "MIT":
        raise SystemExit("Unexpected distribution metadata")
    if info["Version"] not in path.name:
        raise SystemExit("Filename does not match metadata version")
    versions.add(info["Version"])
    for name in names:
        parts = PurePosixPath(name).parts
        if any(part in {".venv", ".release-check", "node_modules", ".git", "lazy", "__pycache__", ".env", ".pypirc", ".npmrc"} for part in parts):
            raise SystemExit(f"Unexpected archive member: {name}")
    print(f"Validated {path.name}: {len(names)} members, MIT license, version {info['Version']}")
if len(versions) != 1:
    raise SystemExit("Wheel and source distribution versions must match")
