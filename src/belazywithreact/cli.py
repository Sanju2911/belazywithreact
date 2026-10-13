from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from .scaffold import ProjectOptions, create_project
from .validators import check_node_tools, resolve_destination

app = typer.Typer(
    name="belazywithreact",
    help="Scaffold a React + TypeScript project with your preferred starter tools.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


@app.callback()
def main() -> None:
    pass


@app.command()
def create(
    name: str = typer.Argument(..., help="Name of the project directory to create."),
    styling: str = typer.Option("both", "--styling", help="Styling setup: css, tailwind, or both."),
    router: bool = typer.Option(True, "--router/--no-router", help="Configure React Router."),
    axios: bool = typer.Option(True, "--axios/--no-axios", help="Install Axios and add an API client."),
    zustand: bool = typer.Option(True, "--zustand/--no-zustand", help="Install Zustand and add an example store."),
    eslint: bool = typer.Option(True, "--eslint/--no-eslint", help="Configure ESLint for TypeScript and React."),
    prettier: bool = typer.Option(True, "--prettier/--no-prettier", help="Install Prettier and add a format script."),
    vitest: bool = typer.Option(True, "--vitest/--no-vitest", help="Install Vitest and add a test script."),
    package_manager: str = typer.Option("npm", "--package-manager", help="Package manager (npm only in v0.1.0)."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation; never overwrite existing paths."),
) -> None:
    styling = styling.lower().strip()
    if styling not in {"css", "tailwind", "both"}:
        console.print("[red]Invalid --styling value.[/red] Choose css, tailwind, or both.")
        raise typer.Exit(code=2)
    package_manager = package_manager.lower().strip()
    if package_manager != "npm":
        console.print("[red]Only npm is supported in version 0.1.0.[/red]")
        raise typer.Exit(code=2)

    try:
        destination = resolve_destination(name, Path.cwd())
        if destination.exists() or destination.is_symlink():
            console.print(f"[red]Destination already exists:[/red] {destination}")
            console.print("Choose a different project name. Existing files will not be overwritten.")
            raise typer.Exit(code=2)
        check_node_tools()
    except (ValueError, RuntimeError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=2) from exc

    options = ProjectOptions(
        styling=styling, router=router, axios=axios, zustand=zustand,
        eslint=eslint, prettier=prettier, vitest=vitest, package_manager=package_manager,
    )
    if not yes:
        console.print(Panel.fit(
            f"[bold]Project:[/bold] {name}\n"
            f"[bold]Styling:[/bold] {styling}\n"
            f"[bold]Router:[/bold] {'yes' if router else 'no'}\n"
            f"[bold]Axios:[/bold] {'yes' if axios else 'no'}\n"
            f"[bold]Zustand:[/bold] {'yes' if zustand else 'no'}\n"
            f"[bold]ESLint:[/bold] {'yes' if eslint else 'no'}\n"
            f"[bold]Prettier:[/bold] {'yes' if prettier else 'no'}\n"
            f"[bold]Vitest:[/bold] {'yes' if vitest else 'no'}\n"
            "[bold]Package manager:[/bold] npm",
            title="belazywithreact setup",
        ))
        if not typer.confirm("Create this project?"):
            console.print("Cancelled.")
            raise typer.Exit()

    try:
        with console.status("[bold green]Creating your React project...[/bold green]"):
            create_project(name, destination, options)
    except KeyboardInterrupt as exc:
        console.print("[yellow]Setup interrupted.[/yellow] Any partial project is preserved; inspect it before retrying.")
        raise typer.Exit(code=130) from exc
    except FileExistsError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=2) from exc
    except Exception as exc:
        console.print(f"[red]Setup failed:[/red] {exc}")
        console.print(
            "The project directory may have been partially created. Inspect it before retrying; "
            "belazywithreact does not delete it automatically."
        )
        raise typer.Exit(code=1) from exc

    console.print(f"\n[bold green]Done![/bold green] Created [cyan]{name}[/cyan].")
    console.print(f"Next:\n  cd {name}\n  npm run dev")
    if vitest:
        console.print("Run tests with: npm test")


if __name__ == "__main__":
    app()
