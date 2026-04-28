import click
from pathlib import Path
from main import cli

class Menu:
    """Interactive menu system for ZettelCore."""
    
    def __init__(self):
        self.notes_dir = Path("notes")
        self.notes_dir.mkdir(exist_ok=True)
    
    def display_menu(self):
        """Display the main menu and handle user choices."""
        while True:
            click.clear()
            click.echo("=== ZettelCore - Personal Knowledge System ===\n")
            click.echo("1. Create new note")
            click.echo("2. Search notes")
            click.echo("3. Resolve wiki links")
            click.echo("4. View notes graph")
            click.echo("5. Show statistics")
            click.echo("6. Exit")
            click.echo()
            
            try:
                choice = click.prompt("Select an option", type=int, default=1)
                
                if choice == 1:
                    self.create_note()
                elif choice == 2:
                    self.search_notes()
                elif choice == 3:
                    self.resolve_links()
                elif choice == 4:
                    self.view_graph()
                elif choice == 5:
                    self.show_stats()
                elif choice == 6:
                    click.echo("Goodbye!")
                    break
                else:
                    click.echo("Invalid option. Please try again.")
                    click.pause()
                    
            except click.Abort:
                click.echo("\nOperation cancelled.")
                break
            except Exception as e:
                click.echo(f"Error: {e}")
                click.pause()
    
    def create_note(self):
        """Handle note creation through interactive prompts."""
        click.clear()
        click.echo("--- Create New Note ---\n")
        
        title = click.prompt("Enter note title (optional)", default="", show_default=False)
        content = click.edit("# New Note\n\nStart writing here...")
        
        if content is None:
            click.echo("Note creation cancelled.")
            click.pause()
            return
        
        # Extract only the user's content, removing the template if it wasn't modified
        template = "# New Note\n\nStart writing here..."
        if content.strip() == template.strip():
            content = ""
        else:
            # Remove the template from the beginning if present
            if content.strip().startswith(template.strip()):
                content = content.replace(template, "", 1)

        tags_input = click.prompt("Enter tags (comma-separated, optional)", default="", show_default=False)
        tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()] if tags_input else []
        
        click.echo("\nCreating note...")
        try:
            # Create argument list for the create command
            args = []
            # Add content as --content flag if it's not empty
            if content and content.strip():
                args.extend(['--content', content.strip()])
            # Add tags option if tags exist
            if tags:
                args.extend(['--tags', ','.join(tags)])
            # Add title option if title exists
            if title:
                args.extend(['--title', title])
            
            # Create a context and invoke the create command
            ctx = cli.make_context('cli', [])
            create_cmd = cli.get_command(ctx, 'create')
            create_ctx = create_cmd.make_context('create', args)
            create_cmd.invoke(create_ctx)
                
        except Exception as e:
            click.echo(f"Error creating note: {e}")
        
        click.pause()
    
    def search_notes(self):
        """Handle note search through interactive prompts."""
        click.clear()
        click.echo("--- Search Notes ---\n")
        
        query = click.prompt("Enter search query (#tag or text)")
        use_rg = click.confirm("Use ripgrep for faster search if available", default=True)
        
        click.echo("\nSearching...")
        click.echo()
        try:
            ctx = cli.make_context('find', [])
            cli.invoke(ctx, query=query, use_rg=use_rg)
        except Exception as e:
            click.echo(f"Error searching notes: {e}")
        
        click.pause()
    
    def resolve_links(self):
        """Handle link resolution."""
        click.clear()
        click.echo("--- Resolve Wiki Links ---\n")
        click.echo("Scanning notes for unresolved wiki links...")
        click.echo()
        
        try:
            ctx = cli.make_context('resolve-links', [])
            cli.invoke(ctx)
        except Exception as e:
            click.echo(f"Error resolving links: {e}")
        
        click.pause()
    
    def view_graph(self):
        """Display the notes graph."""
        click.clear()
        click.echo("--- Notes Graph ---\n")
        click.echo("Loading interactive graph visualization...")
        click.echo("(Press 'q' to exit graph view)\n")
        
        try:
            ctx = cli.make_context('graph', [])
            cli.invoke(ctx)
        except Exception as e:
            click.echo(f"Error displaying graph: {e}")
        
        click.pause()
    
    def show_stats(self):
        """Show collection statistics."""
        click.clear()
        click.echo("--- Statistics ---\n")
        
        try:
            ctx = cli.make_context('stats', [])
            cli.invoke(ctx)
        except Exception as e:
            click.echo(f"Error showing statistics: {e}")
        
        click.pause()