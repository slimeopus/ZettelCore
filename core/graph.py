import os
import glob
import yaml
import re
from typing import Dict, List, Set, Tuple

# Регулярное выражение для поиска вики-ссылок [[...]]
WIKI_LINK_PATTERN = r'\[\[([^\]]+)\]\]'

# Регулярное выражение для поиска тегов #...
TAG_PATTERN = r'#\w+'

Node = str
Edge = Tuple[Node, Node]


class GraphBuilder:
    """
    Строит граф связей между заметками на основе вики-ссылок и тегов.
    """
    
    def __init__(self, notes_dir: str = "notes"):
        self.notes_dir = notes_dir
        self.nodes: Set[Node] = set()
        self.edges: Set[Edge] = set()
        self.node_titles: Dict[Node, str] = {}  # filepath -> title
        
    def extract_links(self, content: str) -> List[str]:
        """Извлекает вики-ссылки из контента."""
        # Находим все совпадения [[link]] или [[link|alias]]
        matches = re.findall(WIKI_LINK_PATTERN, content)
        # Оставляем только имя ссылки (до | если есть)
        return [match.split('|')[0].strip() for match in matches]
        
    def extract_tags(self, content: str) -> List[str]:
        """Извлекает теги из контента."""
        return re.findall(TAG_PATTERN, content)
    
    def get_note_filename(self, title: str) -> str:
        """
        Преобразует заголовок ссылки в имя файла.
        Пока простая эвристика: ищем файл, содержащий заголовок в имени.
        """
        # Убираем расширение, если есть
        if '.' in title:
            title = title.rsplit('.', 1)[0]
        
        for filepath in glob.glob(os.path.join(self.notes_dir, "*.md")):
            filename = os.path.basename(filepath)
            if '.' in filename:
                filename = filename.rsplit('.', 1)[0]
            if title.lower() in filename.lower():
                return filepath
        return None
    
    def build(self) -> Tuple[Set[Node], Set[Edge]]:
        """Строит граф: возвращает узлы и рёбра."""
        self.nodes = set()
        self.edges = set()
        self.node_titles = {}
        
        # Сначала собираем все узлы и их метаданные
        for filepath in glob.glob(os.path.join(self.notes_dir, "*.md")):
            self.nodes.add(filepath)
            # Используем имя файла как заголовок
            self.node_titles[filepath] = os.path.basename(filepath).replace('.md', '')
        
        # Теперь строим связи по вики-ссылкам
        for filepath in self.nodes:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Ищем вики-ссылки
                links = self.extract_links(content)
                for link in links:
                    target = self.get_note_filename(link)
                    if target and target in self.nodes and target != filepath:
                        # Создаём направленное ребро
                        self.edges.add((filepath, target))
                        
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
                continue
        
        # Связи по тегам (опционально, создаёт много рёбер)
        # tag_groups = {}
        # for filepath in self.nodes:
        #     try:
        #         with open(filepath, 'r', encoding='utf-8') as f:
        #             content = f.read()
        #         if content.startswith('---\n'):
        #             second_delimiter = content.find('\n---\n', 4)
        #             if second_delimiter != -1:
        #                 frontmatter = content[4:second_delimiter]
        #                 data = yaml.safe_load(frontmatter)
        #                 if data and 'tags' in data:
        #                     for tag in data['tags']:
        #                         tag_groups.setdefault(tag, []).append(filepath)
        #     except:
        #         continue
        # 
        # for tag, files in tag_groups.items():
        #     for i, file1 in enumerate(files):
        #         for file2 in files[i+1:]:
        #             self.edges.add((file1, file2))
        
        return self.nodes, self.edges