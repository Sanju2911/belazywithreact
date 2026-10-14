# belazywithreact

[![CI](https://github.com/Sanju2911/belazywithreact/actions/workflows/tests.yml/badge.svg)](https://github.com/Sanju2911/belazywithreact/actions/workflows/tests.yml)

A Python CLI that creates a React + TypeScript app with Vite and a useful starter
structure. Version **0.1.0** is the initial release. npm is the supported package
manager.

[PyPI package](https://pypi.org/project/belazywithreact/) ·
[GitHub releases](https://github.com/Sanju2911/belazywithreact/releases)

## Prerequisites

- Python 3.10 or newer.
- An even-numbered Node.js release >=22.13; Node.js 24 LTS is recommended.
- npm on PATH and internet access to download packages from the npm registry.

Check `python --version`, `node --version`, and `npm --version`.

## Installation

Install a published release from PyPI:

```powershell
python -m pip install belazywithreact
belazywithreact --help
```

Install from a local checkout:

```powershell
python -m pip install .
```

For development on Windows, a virtual environment avoids global changes and
does not require changing PowerShell's execution policy:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\belazywithreact.exe --help
```

On macOS/Linux use `python3 -m venv .venv`, then `.venv/bin/python` and
`.venv/bin/belazywithreact` instead.

## Usage

```powershell
belazywithreact create my-app
cd my-app
npm run dev
```

Creation asks for confirmation. `--yes` skips that question and still refuses
to overwrite an existing destination, including an empty directory.

Defaults include CSS + Tailwind CSS 4, React Router, Axios, Zustand, ESLint,
Prettier, and Vitest. Tailwind uses its official Vite plugin and CSS import;
customize its theme in CSS. ESLint is explicitly configured for TypeScript and
React. `npm test` runs once, and `npm run test:watch` starts watch mode.

A minimal CSS app:

```powershell
belazywithreact create my-app --styling css --no-router --no-axios --no-zustand --no-eslint --no-prettier --no-vitest --yes
```

| Option | Default | Behavior |
| --- | --- | --- |
| `--styling css\|tailwind\|both` | `both` | Enables Tailwind in tailwind/both; custom starter CSS is always included |
| `--router` / `--no-router` | enabled | Home and fallback routes with BrowserRouter |
| `--axios` / `--no-axios` | enabled | Axios API client and public API base URL example |
| `--zustand` / `--no-zustand` | enabled | Example counter store |
| `--eslint` / `--no-eslint` | enabled | ESLint config, dependencies, and lint script |
| `--prettier` / `--no-prettier` | enabled | Format script and ignore file |
| `--vitest` / `--no-vitest` | enabled | Test scripts and example unit test |
| `--package-manager npm` | `npm` | Only npm is supported in 0.1.0 |
| `--yes`, `-y` | disabled | Skip confirmation |

Use `belazywithreact create --help` for all options.

## Generated structure

```text
my-app/
  src/
    assets/
    components/Button.tsx
    hooks/
    layouts/
    pages/HomePage.tsx
    services/api.ts          # when Axios is enabled
    store/useAppStore.ts     # when Zustand is enabled
    styles/index.css
    styles/tailwind.css
    types/
    utils/example.test.ts    # when Vitest is enabled
    App.tsx
    main.tsx
  .env.example
  eslint.config.js          # when ESLint is enabled
  vite.config.ts
  package.json
  package-lock.json
  README.md
```

The Button supports native button props and children. Customize the generated
components, folders, API client, and store after creation. Empty starter folders
contain .gitkeep files. The scaffold does not provide authentication, backend
services, deployment, or arbitrary folder/component generation flags.

Validate your generated app:

```powershell
npm ci
npm test
npm run lint
npm run build
```

Test and lint commands require their respective enabled options.
BrowserRouter deployments need a server fallback to index.html for route URLs.
All `VITE_` environment variables are public browser values, never secrets.

## Troubleshooting

- **Missing Node/npm or WinError 2:** install Node.js 24 LTS and reopen the
  terminal so PATH updates. On Windows, check `where.exe node` and
  `where.exe npm`; `npm.cmd --version` should work. The CLI preserves its
  tested `call "<resolved npm.cmd>"` launch method for paths containing spaces.
- **Unsupported Node version:** upgrade to an even-numbered release >=22.13.
  The generated tooling needs a newer Node version than some older Vite releases.
- **Invalid name:** use a directory name starting with a letter or number and
  containing only letters, numbers, dots, underscores, or hyphens. Names cannot
  end in a dot, exceed 214 characters, use Windows device names like CON/LPT1,
  or use npm-reserved names. Path separators and shell operators are rejected.
  Vite normalizes uppercase directory names to valid npm package names.
- **Destination exists:** choose another name; existing files are preserved.
- **npm failure or interruption:** read npm's output and check network/PATH.
  Partial projects are preserved. Inspect them before manually removing or
  repairing them; a retry with the same name will refuse to overwrite them.
- **Dependency advisory:** run `npm audit` and review compatible upgrades;
  do not blindly force a major upgrade.

## Architecture and development

`cli.py` parses options with Typer and prints progress/errors with Rich.
`validators.py` validates names, destination boundaries, and Node prerequisites.
`scaffold.py` invokes create-vite **9.2.1**, writes the starter files, installs
selected tools, updates package.json, and synchronizes package-lock.json. npm
output remains visible, and failures return nonzero status. Interruption during
creation returns 130. The CLI never deletes a partial project automatically.

The Vite creator and optional-tool install requests specify reviewed versions;
Vite's base template and npm semver ranges can still resolve newer compatible
dependencies. Commit the generated lockfile and use `npm ci` for reproducible
app installations. Revalidate dependencies before a future CLI release.

```powershell
python -m pytest
python -m build
python -m twine check --strict dist/*
python scripts/check_dist.py
```

Unit tests mock npm and run offline. CI checks Python 3.10, 3.12, and 3.14 on
Windows, macOS, and Linux, validates distributions, and builds real default and
minimal React apps. See [CONTRIBUTING.md](CONTRIBUTING.md) for contributions,
[SECURITY.md](SECURITY.md) for security reporting, and
[RELEASING.md](RELEASING.md) for TestPyPI-first Trusted Publishing and explicit
production-release approval. GitHub and both package-index accounts must be
configured separately before publication.

## License

[MIT](LICENSE).
