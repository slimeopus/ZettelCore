from textual.app import App
from textual.widgets import Tree, Header, Footer, Button
from textual.containers import Vertical, Horizontal
from textual.events import Click
from core.graph import GraphBuilder


class GraphApp(App):
    """TUI приложение для визуализации графа заметок."""
    
    CSS = """
    Screen {
        layout: vertical;
    }
    Vertical {
        height: 1fr;
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
        
        yield Footer()
    
    def _build_tree(self, tree: Tree, nodes, edges):
        """Строит иерархическое дерево для отображения графа."""
        # Группировка по тегам будет в будущем
        # Пока просто отображаем узлы и связи
        
        # Сначала добавим все узлы
        node_map = {}
        for node in sorted(nodes):
            title = self.builder.node_titles[node]
            branch = tree.root.add(f"● {title}", expand=False)
            node_map[node] = branch
        
        # Теперь добавим рёбра как вложенные элементы
        for source, target in sorted(edges):
            source_title = self.builder.node_titles[source]
            target_title = self.builder.node_titles[target]
            
            if source in node_map:
                node_map[source].add(f"└─→ {target_title}", expand=False)
        
        tree.root.expand()  # Раскрываем корень
    
    def on_key(self, event):
        """Обработка клавиш."""
        if event.key == "q":  # Выход по Q
            self.exit()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Обработка нажатия кнопок."""
        if event.button.id == "exit-btn":
            self.exit()
        elif event.button.id == "refresh-btn":
            self.refresh_graph()
    
    def refresh_graph(self):
        """Обновление графа."""
        tree = self.query_one("#graph-tree", Tree)
        tree.clear()
        self.nodes, self.edges = self.builder.build()
        self._build_tree(tree, self.nodes, self.edges)
        tree.root.expand()

# Альтернативный простой вывод с Rich (для отладки)
from rich.console import Console
from rich.tree import Tree as RichTree

def display_graph_rich():
    """Простая визуализация графа с помощью Rich."""
    console = Console()
    builder = GraphBuilder()
    nodes, edges = builder.build()
    
    console.print(f"[bold green]Graph: {len(nodes)} nodes, {len(edges)} edges[/bold green]\n")
    
    if not nodes:
        console.print("[red]No notes found.[/red]")
        return
    
    tree = RichTree("[bold]Notes Graph[/bold]")
    
    # Группировка по связям
    node_parents = {}
    for source, target in edges:
        source_title = builder.node_titles[source]
        target_title = builder.node_titles[target]
        
        if source not in node_parents:
            node_parents[source] = tree.add(f"[cyan]● {source_title}[/cyan]")
        
        node_parents[source].add(f"[magenta]└─→ {target_title}[/magenta]")
    
    # Узлы без исходящих рёбер
    isolated = [n for n in nodes if n not in node_parents]
    if isolated:
        isolated_tree = tree.add("[yellow]Isolated Notes[/yellow]")
        for node in sorted(isolated):
            title = builder.node_titles[node]
            isolated_tree.add(f"[white]● {title}[/white]")
    
    console.print(tree)