"""CLI interface for Echo agent"""

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from echo import EchoAgent
from echo.config import get_settings

app = typer.Typer(help="Echo - AI Personal Learning Assistant")
console = Console()


@app.command()
def chat(
    user_id: str = typer.Option(None, help="User ID"),
):
    """Start interactive chat with Echo"""
    settings = get_settings()
    user_id = user_id or settings.echo_user_id

    console.print(Panel.fit(
        "[bold blue]Echo - AI Personal Learning Assistant[/bold blue]\n"
        f"User: {user_id}",
        border_style="blue"
    ))
    console.print("Type 'exit' or 'quit' to end the session\n")

    # Initialize agent
    try:
        agent = EchoAgent(user_id=user_id)
    except Exception as e:
        console.print(f"[red]Failed to initialize agent: {e}[/red]")
        raise typer.Exit(1)

    # Chat loop
    while True:
        try:
            # Get user input
            user_input = console.input("[bold green]You:[/bold green] ")

            if user_input.lower() in ["exit", "quit", "bye"]:
                console.print("\n[blue]Goodbye! Keep learning! 📚[/blue]")
                break

            if not user_input.strip():
                continue

            # Get response
            console.print("[bold blue]Echo:[/bold blue] ", end="")
            response = agent.chat(user_input)

            # Display response
            console.print(Markdown(response))
            console.print()

        except KeyboardInterrupt:
            console.print("\n\n[blue]Chat interrupted. Goodbye![/blue]")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]\n")

    # Cleanup
    agent.close()


@app.command()
def learn(
    topic: str = typer.Argument(..., help="Topic to learn"),
    level: str = typer.Option("beginner", help="Current level (beginner/intermediate/advanced)"),
    user_id: str = typer.Option(None, help="User ID"),
):
    """Create a learning path for a topic"""
    settings = get_settings()
    user_id = user_id or settings.echo_user_id

    console.print(f"[blue]Creating learning path for: {topic}[/blue]\n")

    agent = EchoAgent(user_id=user_id)

    try:
        # Build knowledge graph
        console.print("📊 Building knowledge graph...")
        graph = agent.build_knowledge_graph(topic)

        # Create learning path
        console.print("🗺️  Creating learning path...")
        path = agent.create_learning_path(topic, level)

        # Display results
        console.print(Panel.fit(
            f"[bold green]Learning Path Created![/bold green]\n"
            f"Topic: {topic}\n"
            f"Level: {level}",
            border_style="green"
        ))

        console.print("\n[bold]Learning Stages:[/bold]")
        if "stages" in path:
            for i, stage in enumerate(path["stages"], 1):
                console.print(f"\n{i}. {stage.get('name', 'Stage ' + str(i))}")
                console.print(f"   Duration: {stage.get('duration', 'N/A')}")
                if "objectives" in stage:
                    console.print("   Objectives:")
                    for obj in stage["objectives"]:
                        console.print(f"   - {obj}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    finally:
        agent.close()


@app.command()
def add(
    url: str = typer.Argument(..., help="Resource URL to add"),
    tags: str = typer.Option("", help="Comma-separated tags"),
    user_id: str = typer.Option(None, help="User ID"),
):
    """Add a learning resource"""
    settings = get_settings()
    user_id = user_id or settings.echo_user_id

    console.print(f"[blue]Adding resource: {url}[/blue]")

    agent = EchoAgent(user_id=user_id)

    try:
        tag_list = [t.strip() for t in tags.split(",")] if tags else []
        result = agent.add_resource(url, tags=tag_list)

        if "error" in result:
            console.print(f"[red]Error: {result['error']}[/red]")
        else:
            console.print(Panel.fit(
                f"[bold green]Resource Added![/bold green]\n"
                f"Title: {result.get('title', 'N/A')}\n"
                f"File ID: {result.get('file_id', 'N/A')}",
                border_style="green"
            ))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    finally:
        agent.close()


@app.command()
def progress(
    user_id: str = typer.Option(None, help="User ID"),
):
    """Show learning progress"""
    settings = get_settings()
    user_id = user_id or settings.echo_user_id

    agent = EchoAgent(user_id=user_id)

    try:
        prog = agent.get_learning_progress()

        console.print(Panel.fit(
            f"[bold blue]Learning Progress[/bold blue]\n"
            f"Topics: {len(prog.get('topics', []))}\n"
            f"Resources: {prog.get('resources_added', 0)}\n"
            f"Knowledge Points: {prog.get('knowledge_points', 0)}",
            border_style="blue"
        ))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    finally:
        agent.close()


@app.command()
def profile(
    user_id: str = typer.Option(None, help="User ID"),
    user_name: str = typer.Option(None, help="User display name"),
    update: bool = typer.Option(False, "--update", "-u", help="Update profile from NeuroMemory"),
    show: bool = typer.Option(True, "--show", "-s", help="Show profile content"),
    path_only: bool = typer.Option(False, "--path", "-p", help="Show only the profile path"),
):
    """Manage user profile (ECHO.md)"""
    settings = get_settings()
    user_id = user_id or settings.echo_user_id

    agent = EchoAgent(user_id=user_id, user_name=user_name)

    try:
        if path_only:
            # Just show the profile path
            console.print(f"[blue]Profile location:[/blue] {agent.get_profile_path()}")
            return

        if update:
            # Update profile from NeuroMemory
            console.print("[blue]Updating profile from NeuroMemory...[/blue]")
            profile_path = agent.update_profile()

            if profile_path:
                console.print(Panel.fit(
                    f"[bold green]Profile Updated![/bold green]\n"
                    f"Location: {profile_path}",
                    border_style="green"
                ))
            else:
                console.print("[yellow]Profile update failed. See logs for details.[/yellow]")

        if show:
            # Show profile content
            content = agent.profile_content

            if content:
                console.print("\n")
                console.print(Markdown(content))
                console.print("\n")
            else:
                console.print("[yellow]No profile found. Use --update to create one.[/yellow]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    finally:
        agent.close()


if __name__ == "__main__":
    app()
