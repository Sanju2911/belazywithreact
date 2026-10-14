# Validation report — 2026-10-13

## Existing implementation

The project contained a src-layout Hatchling Python package, a Typer/Rich CLI,
name/tool validators, npm/Vite orchestration with inline starter templates,
two Python test files, a Linux-only test workflow, README, MIT license, and an
existing generated `lazy` app. There was no Git repository or configured Git
author. Package and module versions were both 0.1.0; neither was bumped.
All package source, tests, configuration, and documentation were inspected.
The existing generated app and virtual environment were preserved.

## Changes

- Retained the Windows `call "npm.cmd"` subprocess method and added tests for
  paths containing spaces, missing launchers, and shell argument rejection.
- Validated library entry points as well as CLI calls; rejected Windows device
  names, npm-reserved names, long names, invalid styling/package managers,
  existing paths, and symbolic-link destinations.
- Checked Node execution and compatible versions. The default ESLint requires
  at least Node 22.13; even-numbered versions are supported, with 24 recommended.
- Ensured minimal apps install dependencies and lockfiles are synchronized.
- Pinned create-vite to 9.2.1 with noninteractive scaffolding. Specified reviewed
  optional-tool versions; compatible versions can still resolve through npm
  ranges and Vite's base template.
- Replaced the generated entry point's Vite demo CSS import with the starter
  app entry point. Preserved Button/HomePage, router, API client, store, and
  the existing folder structure.
- Migrated Tailwind 3 to Tailwind 4.3.3's official Vite plugin after npm audit
  found seven vulnerable Tailwind 3 dependency entries. The updated app audit
  reported zero vulnerabilities; no security checks were disabled.
- Configured ESLint explicitly because the current Vite template uses Oxlint.
  Removed generated Oxlint dependencies/configuration; honored --no-eslint.
- Made `npm test` a single run and added test:watch. Corrected optional lint
  documentation and added environment-value exclusions to generated .gitignore.
- Preserved partial projects on errors and interruption, with actionable CLI
  errors and exit codes. Restored the missing final paragraph of the MIT license.
- Added packaging metadata and an explicit sdist allowlist; excluded virtual
  environments, caches, generated apps, credentials, and node_modules.
- Added Windows/macOS/Linux Python and React CI, separate OIDC publishing jobs,
  manual TestPyPI and intentional GitHub Release production workflows, action
  SHA pins, distribution/version checks, contribution and security guidance,
  issue/PR templates, Git ignores, and line-ending configuration.

## Checks actually executed

Local environment: Windows, Python 3.12.10, Node 24.14.1, npm 11.11.0.

| Check | Actual result |
| --- | --- |
| Original Python tests | 14 passed, 1 failed (Windows mock did not support shell=True) |
| Updated Python tests | 69 passed |
| Coverage run | 99% overall; scaffold.py 100% |
| `pip install .` in new virtual environment | passed |
| Wheel installation in the new environment | passed |
| Installed CLI --help and npm.cmd launch | passed |
| Default app scaffolding in a path with spaces | passed |
| Default app npm ci | passed |
| Default app npm test | 1 test passed |
| Default app npm run lint (ESLint) | passed |
| Default app npm run build (TypeScript + Vite) | passed |
| Default app npm audit | zero vulnerabilities |
| Minimal app scaffolding and npm ci | passed |
| Minimal app npm run build | passed |
| Minimal app npm audit | zero vulnerabilities |
| Minimal app omitted tool dependencies/scripts | verified |
| python -m build (isolated Hatchling build) | wheel and sdist built |
| python -m twine check --strict dist/* | both passed |
| scripts/check_dist.py | both archives passed; expected source and MIT metadata |
| scripts/check_version.py | 0.1.0 declarations match |
| pip check | no broken requirements |
| Actionlint | all workflow files passed |
| Staged-file review and credential-pattern scan | only intended source/docs/workflows; no credential matches |

The distribution files are `dist/belazywithreact-0.1.0-py3-none-any.whl` and
`dist/belazywithreact-0.1.0.tar.gz`. Obtain their current hashes with
`Get-FileHash dist/* -Algorithm SHA256` after the final build. Artifacts remain
local and ignored by Git. Test-generated apps and their temporary environment
are disposable; the user's existing `lazy` app must remain untouched.

## GitHub verification — 2026-10-14

GitHub CLI authenticated as Sanju2911 after user-approved authorization and
browser email verification. The prepared main branch was pushed to the intended
public repository, and its remote commit SHA matched local HEAD. No force push
or history rewrite was used. Private vulnerability reporting is enabled.

[CI run 38501037718](https://github.com/Sanju2911/belazywithreact/actions/runs/38501037718)
passed all 12 jobs for commit 52b62df905ae02f672a301573d99e1821ef7214d:
nine Python test/package jobs (3.10, 3.12, 3.14 on Windows, macOS, Linux) and
three real React scaffold validation jobs (default app install/test/lint/build
and minimal app build on all three operating systems). Later documentation
commits also trigger CI; see the repository's Actions tab for their current state.

## External state and limitations

No release tag or GitHub Release was created. No package was uploaded to either
index. On 2026-10-13 both package JSON endpoints returned HTTP 404, and the
public repository lookup for the intended owner/name returned 404. A 404 is not
proof that a name can be claimed or that a private repository does not exist.

On 2026-10-14 the browser session was verified as Sanju2911, and the public
repository https://github.com/Sanju2911/belazywithreact was created and verified
empty. Local origin points to that repository. Verified project URLs were added
to package metadata, and all 69 tests and strict distribution checks passed again.
The prepared branch is connected and pushed; GitHub CLI authorization is complete.
The GitHub environments testpypi and pypi were created. Production pypi requires
Sanju2911 review, disables administrator bypass, and accepts only v* tags.
The TestPyPI publishing settings redirect to login; no authenticated index
session or configured Trusted Publisher has been verified.
Remote Actions passed on all configured OS/Python combinations. Python
3.10/3.14, macOS, and Linux were validated in CI rather than on this Windows host.

PyPI and TestPyPI accounts and Trusted Publishers require separate setup.
Configure GitHub environments, especially production required-reviewer
protection, before triggering publishing. Follow [RELEASING.md](RELEASING.md)
for exact fields, TestPyPI verification, and future releases. Production
publication requires the owner's explicit approval after reviewing version,
filenames, hashes, successful validation, CI, and TestPyPI results.
