import click
from .commands import interactive_search_fzf

@click.group()
def cli():
    """ZettelCore CLI"""
    pass

@cli.command()
@click.argument('tag', required=False)
def fzf(tag):
    """Interactive search using fzf"""
    interactive_search_fzf(tag)

@cli.command()
@click.argument('note_id')
@click.option('--editor', default='code', help='Editor command to open the note')
def open(note_id, editor):
    """Open a note by ID for editing"""
    open_note(note_id, editor)