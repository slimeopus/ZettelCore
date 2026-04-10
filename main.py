import datetime

import click
import yaml

from core.editor import process_file_for_autocomplete, remove_suggestions
from core.search import find_notes_by_tag
from core.stats import NoteStats
from core.storage import save_note
from core.tui import GraphApp, display_graph_rich


@click.group()
def cli():
    pass

@cli.command()
@click.argument('text', required=False)
@click.option('--tags', help='Comma-separated tags')
def create(text, tags):
    """Create a new note with automatic filename and frontmatter. Opens in $EDITOR."""
    tag_list = tags.split(',') if tags else []
    # If text is provided and is a simple title, use it as title
    if text and not text.strip().endswith('.') and len(text.split()) <= 6:
        note_path = save_note('', tag_list, title=text.strip())
    else:
        note_path = save_note(text or 'New note', tag_list, title=None)
    click.echo(f"Note created: {note_path}")
    
    # Prepare file for autocomplete
    process_file_for_autocomplete(note_path)
    
    # Open in editor
    import os
    editor = os.getenv('EDITOR', 'code')
    os.system(f'{editor} "{note_path}"')
    
    # Remove suggestions before final save
    remove_suggestions(note_path)

@cli.command()
def resolve_links():
    """Scan all notes for [[wiki-style links]], find missing ones, and offer to create them."""
    import re
    from pathlib import Path

    notes_dir = Path("notes")
    if not notes_dir.exists():
        click.echo("No notes directory found.")
        return

    # Collect all existing note filenames (without .md)
    existing_notes = set()
    for file in notes_dir.glob("*.md"):
        existing_notes.add(file.stem)  # filename without extension

    # Regex to find [[WikiLink]] or [[Target Note|Display Text]]
    link_pattern = re.compile(r'\[\[([^]|]+)(?:\|[^]]+)?]]')
    all_links = set()
    linked_files = {}

    # Scan all note files for links
    for file in notes_dir.glob("*.md"):
        try:
            content = file.read_text(encoding='utf-8')
            matches = link_pattern.findall(content)
            for match in matches:
                all_links.add(match)
                if match not in linked_files:
                    linked_files[match] = []
                linked_files[match].append(file.name)
        except (IOError, OSError) as e:
            click.echo(f"Error reading {file}: {e}")

    # Find links pointing to non-existent notes
    missing_links = all_links - existing_notes
    if not missing_links:
        click.echo("All wiki links are resolved.")
        return

    click.echo(f"Found {len(missing_links)} unresolved link(s):\n")
    for link in sorted(missing_links):
        sources = ', '.join(linked_files[link])
        click.echo(f"• [[{link}]]  (used in: {sources})")

    # Ask user to create missing notes
    click.echo("\nDo you want to create these notes? (y/N): ", nl=False)
    try:
        response = click.get_text_stream('stdin').read().strip().lower()
    except EOFError:
        response = 'n'
    
    if not response:
        response = 'n'
    
    if response not in ('y', 'yes'):
        click.echo("Operation cancelled.")
        return

    # Create missing notes
    for link in missing_links:
        filename = (notes_dir / f"{link}.md")
        if not filename.exists():
            timestamp = datetime.datetime.now()
            note_data = {
                'title': link.replace('-', ' ').title(),
                'date': timestamp.isoformat(),
                'tags': []
            }
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write('---\n')
                    yaml.dump(note_data, f, allow_unicode=True)
                    f.write('---\n\n')
                    f.write(f"This is a stub for '{link}'.\n")
                click.echo(f"Created: {filename}")
            except Exception as e:
                click.echo(f"Error creating {filename}: {e}", err=True)

@cli.command()
@click.argument('query')
@click.option('--use-rg', is_flag=True, help='Use ripgrep for faster search if available')
def find(query, use_rg=False):
    """Find notes by tag with #tag or by full-text search."""
    import os
    import subprocess
    import glob
    notes_dir = "notes"
    
    # Search by tag
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
        return
    
    # Full-text search
    click.echo(f"Searching text for: '{query}'...\n")
    
    # Try using ripgrep if available and requested
    if use_rg:
        try:
            result = subprocess.run([
                'rg', '--color=never', '--ignore-case', '--files-with-matches', 
                query, notes_dir
            ], capture_output=True, text=True, check=True)
            
            if result.stdout.strip():
                filepaths = result.stdout.strip().split('\n')
            else:
                filepaths = []
        except (subprocess.CalledProcessError, FileNotFoundError):
            click.echo("ripgrep (rg) not available, falling back to Python search...\n")
            filepaths = []
    else:
        filepaths = []
    
    # Fallback to Python search if rg not used or failed
    if not filepaths:
        filepaths = []
        for filepath in glob.glob(os.path.join(notes_dir, "*.md")):
            try:
                content = open(filepath, 'r', encoding='utf-8').read()
                # Skip frontmatter
                if content.startswith('---\n'):
                    second_delimiter = content.find('\n---\n', 4)
                    if second_delimiter != -1:
                        content = content[second_delimiter + 5:]
                
                if query.lower() in content.lower():
                    filepaths.append(filepath)
            except (IOError, OSError) as e:
                click.echo(f"Error reading {filepath}: {e}", err=True)
    
    if not filepaths:
        click.echo("No notes found containing the search term.")
        return
    
    # Display results with snippet
    for filepath in filepaths:
        try:
            content = open(filepath, 'r', encoding='utf-8').read()
            # Skip frontmatter when searching for snippet
            display_content = content
            if content.startswith('---\n'):
                second_delimiter = content.find('\n---\n', 4)
                if second_delimiter != -1:
                    display_content = content[second_delimiter + 5:]
            
            # Find line with query
            lines = display_content.split('\n')
            match_line = next((line for line in lines if query.lower() in line.lower()), None)
            
            # Extract title
            title = os.path.basename(filepath).replace('.md', '')
            if content.startswith('---\n'):
                second_delimiter = content.find('\n---\n', 4)
                if second_delimiter != -1:
                    frontmatter = content[4:second_delimiter]
                    try:
                        data = yaml.safe_load(frontmatter)
                        if data and 'title' in data:
                            title = data['title']
                    except yaml.YAMLError:
                        pass
            
            click.echo(f"• {title}")
            click.echo(f"  {match_line.strip()}")
            click.echo(f"  {filepath}\n")
            
        except (IOError, OSError, yaml.YAMLError) as e:
            click.echo(f"Error processing {filepath}: {e}", err=True)

@cli.command()
def graph():
    """Build and display the notes graph in TUI."""
    try:
        app = GraphApp()
        app.run()
    except ImportError:
        click.echo("Textual not available, falling back to rich...")
        display_graph_rich()
    except (ImportError, ModuleNotFoundError) as e:
        click.echo(f"Error displaying graph: {e}")

@cli.command()
def stats():
    """Display statistics about the notes collection."""
    stats_calculator = NoteStats()
    note_stats = stats_calculator.calculate()
    
    click.echo("Statistics:")
    click.echo(f"- Total notes: {note_stats['total_notes']}")
    click.echo(f"- Tags used: {note_stats['unique_tags']}")
    
    if stats['most_linked_note']:
        note = stats['most_linked_note']
        click.echo(f"- Most linked note: {note['title']} ({note['link_count']} incoming)")
    else:
        click.echo("- Most linked note: None")
        
    click.echo(f"- Average links per note: {stats['average_links']:.1f}")
    click.echo(f"- Notes with tags: {stats['notes_with_tags']}/{stats['total_notes']}")

if __name__ == '__main__':
    cli()