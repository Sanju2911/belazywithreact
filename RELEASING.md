# Releasing belazywithreact

The first release candidate is **0.1.0**, retaining the existing version.
No tag or PyPI publication is implied by these instructions. On 2026-10-13,
the PyPI and TestPyPI JSON endpoints returned 404 for this name. That does not
guarantee name availability: pending publishers do not reserve names.
Check again immediately before publishing. Do not replace a project owned by
someone else or attempt to reuse an already uploaded version/file.

On 2026-10-14, production PyPI's pending publisher was registered with explicit
approval for configuration only. TestPyPI's publisher was registered and its
workflow successfully published 0.1.0 from commit 590bfb9; clean-environment
installation, package origin, dependency checks, and CLI execution were verified.
Production publication still requires separate explicit approval. The final
release documentation was updated afterward; the tested CLI source is preserved.

## GitHub setup

The public repository is [Sanju2911/belazywithreact](https://github.com/Sanju2911/belazywithreact),
created and verified on 2026-10-14.
Do not initialize a second README, license, or .gitignore remotely. Verify
`git remote -v` before setting origin and pushing `main`; never force-push.
Update project URLs in pyproject.toml only after verifying the repository exists.
Wait for the **CI** workflow to pass, including all three operating systems.

The GitHub environments **testpypi** and **pypi** were created on 2026-10-14.
The **pypi** environment requires review by **Sanju2911**, disallows administrator
bypass, and permits only tags matching `v*`. Self-review remains allowed so the
sole maintainer can approve a release. Verify these protections under Settings >
Environments before each production release. Environment names in PyPI
configuration must match the workflow exactly.

The workflow file alone does not create these protections. If they are removed,
publishing a non-prerelease GitHub Release could start the production upload.
Do not publish a GitHub Release until the final artifacts have been reviewed and
the owner has explicitly approved production publication.

## Account and Trusted Publisher setup

Create/access your accounts directly at [PyPI](https://pypi.org/account/register/)
and [TestPyPI](https://test.pypi.org/account/register/). They are separate services.
Verify email and complete their required account security setup. Never paste
passwords, tokens, or recovery codes into chat or repository files.

For a new package, use the account's **Publishing** page to add a pending
GitHub publisher. For an existing package you own, use its **Publishing** settings.
Set these fields separately for each service:

| Field | Production PyPI | TestPyPI |
| --- | --- | --- |
| PyPI project name | `belazywithreact` | `belazywithreact` |
| GitHub owner | `Sanju2911` | `Sanju2911` |
| GitHub repository | `belazywithreact` | `belazywithreact` |
| Workflow filename | `publish.yml` | `testpypi.yml` |
| GitHub environment | `pypi` | `testpypi` |

The workflow filename is the basename, not `.github/workflows/publish.yml`.
OIDC uses `id-token: write` only in the upload job. Build jobs have read-only
repository access. No API-token secrets are needed. Actions are pinned to
verified commit SHAs; review and update those pins periodically.

## Local validation

Use Python 3.12 for release scripts, in a development virtual environment:

```powershell
python -m pip install --upgrade build twine
python -m pip install -e ".[dev]"
python -m pytest
python scripts/check_version.py
python -m build
python -m twine check --strict dist/*
python scripts/check_dist.py
Get-FileHash dist/* -Algorithm SHA256
```

Keep dist limited to the current wheel and sdist. Move old artifacts aside before
building another version. The upload-set checker rejects extra files.
Check that wheel metadata, README, license and verified project URLs are correct.
Test the wheel in a new venv, then run `belazywithreact --help` and scaffold an app.
For the generated default app run `npm ci`, `npm test`, `npm run lint`, and
`npm run build`. Also build with all optional features disabled.

## TestPyPI first

After configuring its publisher and environment and authorizing a test upload,
run GitHub Actions > **Publish to TestPyPI** > **Run workflow**, selecting the
reviewed branch/ref. This manual workflow never publishes to production.
Check the upload job result and inspect the actual TestPyPI package page.

Use a clean environment to verify that the artifact comes from TestPyPI:

```powershell
py -m venv .testpypi-venv
.\.testpypi-venv\Scripts\python.exe -m pip install --index-url https://test.pypi.org/simple/ --no-deps belazywithreact==0.1.0
.\.testpypi-venv\Scripts\python.exe -m pip install --index-url https://pypi.org/simple/ "typer>=0.12,<1" "rich>=13.7,<15"
.\.testpypi-venv\Scripts\python.exe -m pip check
.\.testpypi-venv\Scripts\belazywithreact.exe --help
```

Then scaffold and validate an app. Installing the package without dependencies
first ensures its origin; dependencies are obtained separately from normal PyPI.
The conventional alternative is `--index-url https://test.pypi.org/simple/
--extra-index-url https://pypi.org/simple/`, but pip combines indexes without
prioritizing the primary one. Confirm the downloaded artifact's source if using it.

## First production release

Show the owner: version **0.1.0**, the two filenames
`belazywithreact-0.1.0-py3-none-any.whl` and `belazywithreact-0.1.0.tar.gz`,
their SHA256 hashes, local validation, successful CI, and TestPyPI verification.
Obtain explicit approval for the exact action: create tag `v0.1.0` at the reviewed
commit and publish a non-prerelease GitHub Release for that tag, triggering
`publish.yml`; then approve the protected **pypi** environment upload job.
Do not perform this action merely because the repository is ready.

The production workflow tests, verifies tag/version consistency, builds, checks,
and transfers only those two distributions to a separate publishing job.
Prereleases are ignored. After upload, verify the actual PyPI project page and
install `belazywithreact==0.1.0` from normal PyPI in a clean environment. An
existing workflow or green build is not evidence of successful publication.

## Future versions

Update `project.version` in pyproject.toml and `__version__` in
src/belazywithreact/__init__.py together. Document the changes, repeat validation,
commit and push, wait for CI, publish to TestPyPI, and obtain production approval.
Create a matching `v<version>` release tag only after approval. Never overwrite
or re-upload an existing release's files; fixes require a new version.

Official references:

- [PyPI pending publishers](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/)
- [PyPI OIDC publishing and TestPyPI endpoint](https://docs.pypi.org/trusted-publishers/using-a-publisher/)
- [Python Packaging workflow guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [GitHub environment protection](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments)
- [Official PyPA publishing action](https://github.com/pypa/gh-action-pypi-publish)
