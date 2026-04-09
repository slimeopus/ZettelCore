import click
from core.storage import save_note
from core.search import find_notes_by_tag
from core.graph import GraphBuilder
from core.tui import GraphApp, display_graph_rich

@click.group()
def cli():
    pass

@cli.command()
@click.argument('text')
@click.option('--tags', help='Comma-separated tags')
def create(text, tags):
    """Create a new note."""
    tag_list = tags.split(',') if tags else []
    save_note(text, tag_list)
    click.echo("Note saved.")

@cli.command()
@click.argument('query')
def find(query):
    """Find notes by tag. Use #tag syntax."""
    if query.startswith('#'):
        results = find_notes_by_tag(query)
        
        if not results:
            click.echo(f"No notes found with tag '{query}'")
            return
        
        click.echo(f"Found {len(results)} note(s) with tag '{query}':\n")
        for note in results:
            click.echo(f"• {note['title']} [{note['date'][:10]}]")
            click.echo(f"  Tags: {', '.join(note['tags'])}")
            click.echo(f"  Path: {note['path']}\n")
    else:
        click.echo("Please use #tag syntax, e.g., note find #python")

@cli.command()
def graph():
    """Build and display the notes graph in TUI."""
    try:
        app = GraphApp()
        app.run()
    except ImportError:
        click.echo("Textual not available, falling back to rich...")
        display_graph_rich()
    except Exception as e:
        click.echo(f"Error displaying graph: {e}")

if __name__ == '__main__':
    cli()