import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .validators import resolve_destination

CREATE_VITE_VERSION = "9.2.1"
_IS_WINDOWS = os.name == "nt"

Runner = Callable[..., subprocess.CompletedProcess]


@dataclass(frozen=True)
class ProjectOptions:
    styling: str = "both"
    router: bool = True
    axios: bool = True
    zustand: bool = True
    eslint: bool = True
    prettier: bool = True
    vitest: bool = True
    package_manager: str = "npm"


def run_command(
    command: list[str],
    *,
    cwd: Path | None = None,
    runner: Runner = subprocess.run,
) -> None:
    """Run commands cross-platform, including Windows npm .cmd launchers."""
    working_directory = str(cwd) if cwd else None

    if _IS_WINDOWS and command and command[0].lower() == "npm":
        npm_cmd = shutil.which("npm.cmd") or shutil.which("npm")

        if not npm_cmd:
            raise FileNotFoundError(
                "Cannot find npm.cmd. Install Node.js LTS "
                "and reopen PowerShell."
            )

        # list2cmdline quotes spaces but does not escape cmd.exe operators.
        # Keep the working CALL/npm.cmd invocation; reject shell syntax first.
        if any(re.search(r'[&|<>^%!"\r\n]', arg) for arg in command[1:]):
            raise ValueError("Unsafe shell characters in npm arguments.")
        args = subprocess.list2cmdline(command[1:])
        command_line = f'call "{npm_cmd}" {args}'

        runner(
            command_line,
            cwd=working_directory,
            check=True,
            shell=True,
        )
        return

    runner(
        command,
        cwd=working_directory,
        check=True,
    )


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def _add_gitkeep(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    if not any(path.iterdir()):
        (path / ".gitkeep").write_text("", encoding="utf-8")


def configure_project(destination: Path, options: ProjectOptions) -> None:
    src = destination / "src"
    gitignore = destination / ".gitignore"
    existing_ignore = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    _write(gitignore, existing_ignore.rstrip() + "\n\n# Local environment values\n.env\n.env.*\n!.env.example\n")
    for folder in ("assets", "components", "hooks", "layouts", "pages", "services", "store", "types", "utils"):
        _add_gitkeep(src / folder)

    _write(src / "components" / "Button.tsx", '''import type { ButtonHTMLAttributes, PropsWithChildren } from "react";

type ButtonProps = PropsWithChildren<ButtonHTMLAttributes<HTMLButtonElement>>;

export function Button({ children, className = "", ...props }: ButtonProps) {
  return (
    <button className={`app-button ${className}`.trim()} {...props}>
      {children}
    </button>
  );
}
''')
    _write(src / "pages" / "HomePage.tsx", '''import { Button } from "../components/Button";

export function HomePage() {
  return (
    <main className="page">
      <p className="eyebrow">Your project is ready</p>
      <h1>Build something great.</h1>
      <p className="intro">
        This React + TypeScript starter was created with belazywithreact.
      </p>
      <Button onClick={() => window.alert("Your setup is working!")}>
        Test the starter
      </Button>
    </main>
  );
}
''')

    css = '''@import "./tailwind.css";

:root {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: #172033;
  background: #f6f8fc;
  font-synthesis: none;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
}
* { box-sizing: border-box; }
body { margin: 0; min-width: 320px; min-height: 100vh; }
button { font: inherit; }
.page {
  width: min(760px, calc(100% - 40px));
  margin: 12vh auto;
  padding: clamp(24px, 5vw, 56px);
  border: 1px solid #e1e7f0;
  border-radius: 28px;
  background: white;
  box-shadow: 0 24px 70px rgb(31 49 82 / 9%);
}
.eyebrow { color: #6558d3; font-size: .8rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
h1 { margin: 12px 0; font-size: clamp(2.2rem, 6vw, 4rem); letter-spacing: -.055em; line-height: 1.05; }
.intro { max-width: 560px; color: #59657a; font-size: 1.1rem; line-height: 1.7; }
.app-button { margin-top: 18px; padding: 12px 18px; color: white; background: #5145cd; border: 0; border-radius: 12px; cursor: pointer; font-weight: 700; }
.app-button:hover { background: #4035b2; }
'''
    if options.styling in {"tailwind", "both"}:
        _write(src / "styles" / "tailwind.css", '@import "tailwindcss";')
        _write(destination / "vite.config.ts", '''import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";

export default defineConfig({ plugins: [react(), tailwindcss()] });
''')
    else:
        _write(src / "styles" / "tailwind.css", "/* Tailwind is disabled for this project. */")

    _write(src / "styles" / "index.css", css)
    app_content = '''import "./styles/index.css";
import { HomePage } from "./pages/HomePage";

export default function App() {
  return <HomePage />;
}
'''
    if options.router:
        app_content = '''import { BrowserRouter, Route, Routes } from "react-router-dom";
import "./styles/index.css";
import { HomePage } from "./pages/HomePage";

function NotFoundPage() {
  return <main className="page"><h1>Page not found</h1><p>Check the URL and try again.</p></main>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}
'''
    _write(src / "App.tsx", app_content)
    _write(src / "main.tsx", '''import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

createRoot(document.getElementById("root")!).render(
  <StrictMode><App /></StrictMode>,
);
''')
    if options.eslint:
        _write(destination / "eslint.config.js", '''import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import tseslint from "typescript-eslint";
import { defineConfig, globalIgnores } from "eslint/config";

export default defineConfig([
  globalIgnores(["dist", "coverage"]),
  {
    files: ["**/*.{ts,tsx}"],
    extends: [js.configs.recommended, tseslint.configs.recommended,
      reactHooks.configs.flat.recommended, reactRefresh.configs.vite],
    languageOptions: { globals: globals.browser },
  },
]);
''')

    if options.axios:
        _write(src / "services" / "api.ts", '''import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "",
  timeout: 15_000,
  headers: { "Content-Type": "application/json" },
});
''')
        _write(destination / ".env.example", "VITE_API_BASE_URL=https://api.example.com")
    else:
        _write(destination / ".env.example", "# Add VITE_ prefixed public environment variables here.")

    if options.zustand:
        _write(src / "store" / "useAppStore.ts", '''import { create } from "zustand";

type AppState = {
  count: number;
  increment: () => void;
  reset: () => void;
};

export const useAppStore = create<AppState>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  reset: () => set({ count: 0 }),
}));
''')

    if options.vitest:
        _write(src / "utils" / "example.test.ts", '''import { describe, expect, it } from "vitest";

describe("starter test", () => {
  it("runs Vitest successfully", () => {
    expect(1 + 1).toBe(2);
  });
});
''')

    test_script = '\n- `npm test` — run Vitest' if options.vitest else ""
    format_script = '\n- `npm run format` — format files with Prettier' if options.prettier else ""
    lint_script = '\n- `npm run lint` — run ESLint' if options.eslint else ""
    readme = f'''# {destination.name}

React + TypeScript starter generated by **belazywithreact**.

## Start development

```bash
npm run dev
```

## Available scripts

- `npm run dev` — start the Vite development server
- `npm run build` — type-check and build for production{lint_script}{test_script}{format_script}

## Project structure

- `src/components` — reusable UI components
- `src/pages` — route-level pages
- `src/hooks` — reusable React hooks
- `src/services` — API clients and service functions
- `src/store` — client-side state
- `src/styles` — global CSS and Tailwind entry point
- `src/utils` — shared utilities
'''
    _write(destination / "README.md", readme)


def create_project(name: str, destination: Path, options: ProjectOptions, *, runner: Runner = subprocess.run) -> None:
    if options.package_manager != "npm":
        raise ValueError("Only npm is supported in belazywithreact 0.1.0.")
    if options.styling not in {"css", "tailwind", "both"}:
        raise ValueError("Styling must be css, tailwind, or both.")
    # Validate library callers too, before any shell command or file write.
    if destination.is_symlink() or destination.exists():
        raise FileExistsError(
            f"Destination already exists: {destination}. Choose another name; existing files are never overwritten."
        )
    if resolve_destination(name, destination.parent) != destination.resolve():
        raise ValueError("Project name must match the destination directory.")

    run_command(
        ["npm", "create", f"vite@{CREATE_VITE_VERSION}", name, "--", "--template", "react-ts", "--no-interactive"],
        cwd=destination.parent,
        runner=runner,
    )
    if not destination.is_dir():
        raise RuntimeError("Vite completed without creating the expected directory. Check npm output.")

    configure_project(destination, options)

    dependencies: list[str] = []
    dev_dependencies: list[str] = []
    if options.router:
        dependencies.append("react-router-dom@7.18.4")
    if options.axios:
        dependencies.append("axios@1.20.0")
    if options.zustand:
        dependencies.append("zustand@5.0.15")
    if options.styling in {"tailwind", "both"}:
        dev_dependencies.extend(["tailwindcss@4.3.3", "@tailwindcss/vite@4.3.3"])
    if options.eslint:
        dev_dependencies.extend(["eslint@10.12.0", "@eslint/js@10.0.1", "typescript-eslint@8.71.2",
                                 "globals@17.13.0", "eslint-plugin-react-hooks@7.1.1",
                                 "eslint-plugin-react-refresh@0.5.7"])
    if options.prettier:
        dev_dependencies.append("prettier@3.9.10")
    if options.vitest:
        dev_dependencies.append("vitest@5.0.4")

    if dependencies:
        run_command(["npm", "install", *dependencies], cwd=destination, runner=runner)
    if dev_dependencies:
        run_command(["npm", "install", "--save-dev", *dev_dependencies], cwd=destination, runner=runner)

    package_json_path = destination / "package.json"
    package_data = json.loads(package_json_path.read_text(encoding="utf-8"))
    scripts = package_data.setdefault("scripts", {})
    # Current Vite templates use Oxlint. Explicitly honor the ESLint option.
    for section in ("dependencies", "devDependencies"):
        package_data.get(section, {}).pop("oxlint", None)
        package_data.get(section, {}).pop("oxlint-tsgolint", None)
    for config_name in (".oxlintrc.json", "oxlint.config.ts"):
        (destination / config_name).unlink(missing_ok=True)
    if options.eslint:
        scripts["lint"] = "eslint ."
    if options.vitest:
        scripts["test"] = "vitest run"
        scripts["test:watch"] = "vitest"
    if options.prettier:
        scripts["format"] = "prettier --write ."
        _write(destination / ".prettierignore", "node_modules\ndist\ncoverage\npackage-lock.json\n")

    if not options.eslint:
        scripts.pop("lint", None)
        for config_name in ("eslint.config.js", "eslint.config.mjs", ".eslintrc", ".eslintrc.json"):
            config_path = destination / config_name
            if config_path.exists():
                config_path.unlink()
        eslint_packages = {
            "eslint", "@eslint/js", "eslint-plugin-react-hooks",
            "eslint-plugin-react-refresh", "typescript-eslint", "globals",
        }
        for section in ("dependencies", "devDependencies"):
            packages = package_data.get(section, {})
            for package_name in eslint_packages:
                packages.pop(package_name, None)

    package_json_path.write_text(json.dumps(package_data, indent=2) + "\n", encoding="utf-8")
    # Always install: minimal projects have no optional installation commands.
    # This also synchronizes the lockfile after removing optional tooling.
    run_command(["npm", "install"], cwd=destination, runner=runner)
