import os
import yaml
import glob
from typing import List, Dict, Optional

def find_notes_by_tag(tag: str, notes_dir: str = "notes") -> List[Dict[str, str]]:
    """
    Find notes containing a specific tag.
    
    Args:
        tag: The tag to search for (with or without # prefix)
        notes_dir: Directory where notes are stored
    
    Returns:
        List of dictionaries with note metadata and path
    """
    # Remove # prefix if present
    clean_tag = tag.lstrip('#')
    
    results = []
    # Search all markdown files
    for filepath in glob.glob(os.path.join(notes_dir, "*.md")):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse YAML frontmatter (between ---)
            if content.startswith('---\n'):
                second_delimiter = content.find('\n---\n', 4)
                if second_delimiter != -1:
                    frontmatter = content[4:second_delimiter]
                    try:
                        data = yaml.safe_load(frontmatter)
                        if data and 'tags' in data:
                            if clean_tag in data['tags']:
                                results.append({
                                    'title': os.path.basename(filepath).replace('.md', ''),
                                    'path': filepath,
                                    'date': data.get('date', ''),
                                    'tags': data.get('tags', [])
                                })
                    except yaml.YAMLError:
                        continue
        except Exception:
            continue
    
    return results