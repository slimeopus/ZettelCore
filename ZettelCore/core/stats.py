import glob
import os
import re
from collections import defaultdict
from typing import Dict, List

import yaml

from core.graph import GraphBuilder


class NoteStats:
    """
    Calculates statistics about the notes collection.
    """
    
    def __init__(self, notes_dir: str = "notes"):
        self.notes_dir = notes_dir
        self.graph_builder = GraphBuilder(notes_dir)
        
    def get_note_files(self) -> List[str]:
        """Get all note files."""
        return glob.glob(os.path.join(self.notes_dir, "*.md"))
        
    @staticmethod
    def extract_tags_from_content(content: str) -> List[str]:
        """Extract tags from content using regex."""
        return re.findall(r'#\w+', content)
    
    @staticmethod
    def get_note_metadata(filepath: str) -> Dict:
        """Extract metadata from note frontmatter."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if content.startswith('---\n'):
                second_delimiter = content.find('\n---\n', 4)
                if second_delimiter != -1:
                    frontmatter = content[4:second_delimiter]
                    try:
                        data = yaml.safe_load(frontmatter)
                        if data is None:
                            data = {}
                        if 'title' not in data:
                            filename = os.path.basename(filepath)
                            data['title'] = filename.replace('.md', '').replace('-', ' ').title()
                        if 'tags' not in data:
                            data['tags'] = []
                        return data
                    except yaml.YAMLError as e:
                        print(f"YAML error in {filepath}: {e}")
                        pass
            
            # Fallback: use filename as title
            filename = os.path.basename(filepath)
            title = filename.replace('.md', '').replace('-', ' ').title()
            return {'title': title, 'tags': []}
            
        except (IOError, OSError) as e:
            print(f"Error reading {filepath}: {e}")
            return {'title': os.path.basename(filepath).replace('.md', ''), 'tags': []}
    
    def calculate(self) -> Dict[str, any]:
        """
        Calculate all statistics.
        """
        note_files = self.get_note_files()
        
        if not note_files:
            return {
                'total_notes': 0,
                'unique_tags': 0,
                'most_linked_note': None,
                'average_links': 0,
                'notes_with_tags': 0
            }
        
        # Total number of notes
        total_notes = len(note_files)
        
        # Count unique tags and notes with tags
        all_tags = set()
        notes_with_tags = 0
        
        # Extract tags from both frontmatter and content
        for filepath in note_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Get tags from frontmatter
                metadata = self.get_note_metadata(filepath)
                frontmatter_tags = set(metadata.get('tags', []))
                
                # Get tags from content
                content_tags = set(self.extract_tags_from_content(content))
                
                # Combine tags
                all_note_tags = frontmatter_tags.union(content_tags)
                if all_note_tags:
                    notes_with_tags += 1
                    
                all_tags.update(all_note_tags)
                
            except (IOError, OSError) as e:
                print(f"Error processing {filepath}: {e}")
                continue
        
        unique_tags = len(all_tags)
        
        # Build graph to analyze links
        nodes, edges = self.graph_builder.build()
        
        # Count incoming links for each note
        incoming_links = defaultdict(int)
        for source, target in edges:
            incoming_links[target] += 1
        
        # Find most linked note
        most_linked_note = None
        
        if incoming_links:
            most_linked_path = max(incoming_links, key=incoming_links.get)
            most_linked_metadata = NoteStats.get_note_metadata(most_linked_path)
            most_linked_note = {
                'title': most_linked_metadata['title'],
                'path': most_linked_path,
                'link_count': incoming_links[most_linked_path]
            }
        
        # Calculate average number of links per note
        total_outgoing_links = len(edges)
        average_links = total_outgoing_links / total_notes if total_notes > 0 else 0
        
        return {
            'total_notes': total_notes,
            'unique_tags': unique_tags,
            'most_linked_note': most_linked_note,
            'average_links': average_links,
            'notes_with_tags': notes_with_tags
        }
