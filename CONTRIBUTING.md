# Contributing

Use Python 3.10+ and an even-numbered Node.js release >=22.13 (24 LTS recommended).
The release scripts use Python 3.12. Clone the repository, then create a virtual
environment. On Windows no activation or execution-policy change is necessary:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
```

On macOS/Linux use `python3 -m venv .venv` and `.venv/bin/python` instead.

Keep changes focused and describe their behavior and validation in a pull request.
Tests mock npm for offline unit checks. Add regression tests for fixes, including
Windows launcher behavior where relevant. Do not replace the `call "npm.cmd"`
launcher without testing it on Windows with paths containing spaces.

Before proposing a release, run the checks in [RELEASING.md](RELEASING.md).
Test a generated default app with `npm ci`, `npm test`, `npm run lint`, and
`npm run build`; also build a minimal app with all optional tools disabled.
Never commit generated apps, node_modules, secrets, or virtual environments.
Update both Python version declarations together when a release requires a bump.

Treat other contributors respectfully. Offer specific, constructive feedback;
harassment, discrimination, threats, and disclosure of private information are
not welcome. Maintainers may remove inappropriate content and restrict participation.
For security concerns, follow [SECURITY.md](SECURITY.md).
