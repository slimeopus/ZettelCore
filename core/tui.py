from textual.app import App
from textual.widgets import Tree, Header, Footer, Button, Input
from textual.containers import Vertical, Horizontal
from textual.events import Click
from core.graph import GraphBuilder

class GraphApp(App):
    """TUI application for visualizing the notes graph."""
    
    CSS = """
    Screen {
        layout: vertical;
    }
    
    Vertical {
        height: 1fr;
    }
    
    # Hide input widget by default
    Input {
        display: none;
    }
    
    Input:focus {
        display: block;
        dock: top;
        height: 3;
        margin: 1 2;
        background: $surface;
        border: tall $primary;
        border-title-align: center;
        border-title: "Search notes";
    }
    """
    
    def __init__(self):
        super().__init__()
        self.builder = GraphBuilder()
        self.nodes, self.edges = self.builder.build()
        
    def compose(self):
        yield Header()
        
        with Vertical():
            tree = Tree("Notes Graph", id="graph-tree")
            self._build_tree(tree, self.nodes, self.edges)
            yield tree
        
        with Horizontal(id="buttons-container"):
            yield Button("Refresh", id="refresh-btn", variant="primary")
            yield Button("Exit", id="exit-btn", variant="error")
        
        # Search input widget (hidden by default)
        yield Input(placeholder="Enter search term...", id="search-input")
        
        yield Footer()
    
    def _build_tree(self, tree: Tree, nodes, edges, filter_text: str = ""):
        """Build hierarchical tree for graph visualization with optional filtering."""
        tree.clear()
        node_map = {}

        # Filter nodes by title if search term is provided
        filtered_nodes = [
            node for node in nodes
            if filter_text.lower() in self.builder.node_titles[node].lower()
        ]

        # Add all nodes
        for node in sorted(filtered_nodes):
            title = self.builder.node_titles[node]
            branch = tree.root.add(f"● {title}", expand=False)
            node_map[node] = branch
        
        # Add edges as nested items
        for source, target in sorted(edges):
            if source in node_map:
                target_title = self.builder.node_titles[target]
                node_map[source].add(f"└─→ {target_title}", expand=False)
        
        tree.root.expand()  # Expand root
    
    def on_key(self, event):
        """Handle key events."""
        tree = self.query_one("#graph-tree", Tree)
        search_input = self.query_one("#search-input", Input)

        if search_input.has_focus:
            if event.key == "escape":
                search_input.value = ""
                search_input.display = False
                tree.focus()
            return

        if event.key == "up":
            self.action_cursor_up()
        elif event.key == "down":
            self.action_cursor_down()
        elif event.key == "enter":
            self.open_selected_note()
        elif event.key == "/":
            self.action_filter()
        elif event.key == "q":  # Exit on Q
            self.exit()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "exit-btn":
            self.exit()
        elif event.button.id == "refresh-btn":
            self.refresh_graph()
    
    def refresh_graph(self):
        """Refresh the graph."""
        tree = self.query_one("#graph-tree", Tree)
        search_input = self.query_one("#search-input", Input)
        filter_text = search_input.value if search_input.display else ""
        
        tree.clear()
        self.nodes, self.edges = self.builder.build()
        self._build_tree(tree, self.nodes, self.edges, filter_text)
        tree.root.expand()
        
    def open_selected_note(self):
        """Open selected note."""
        tree = self.query_one("#graph-tree", Tree)
        cursor_node = tree.cursor_node
        if cursor_node and cursor_node.data is not None:
            # Placeholder — will open in editor in the future
            self.notify(f"Opening note: {cursor_node.label}")
    
    def action_cursor_up(self) -> None:
        """Move cursor up with boundary check."""
        tree = self.query_one("#graph-tree", Tree)
        if tree.cursor_line > 0:
            tree.cursor_up()
            tree.scroll_to_cursor()

    def action_cursor_down(self) -> None:
        """Move cursor down with boundary check."""
        tree = self.query_one("#graph-tree", Tree)
        if tree.cursor_line < len(tree._nodes) - 1:
            tree.cursor_down()
            tree.scroll_to_cursor()

    def action_filter(self) -> None:
        """Activate search input on / key."""
        search_input = self.query_one("#search-input", Input)
        search_input.display = True
        search_input.focus()
        self.notify("Type to search notes, Esc to cancel")
