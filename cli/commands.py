import os
import subprocess
import sys
import glob
import yaml
from typing import Optional, List
from core.search import find_notes_by_tag

def interactive_search_fzf(tag: Optional[str] = None):
    """
    Interactive search using fzf.
    
    Args:
        tag: Optional tag to filter notes
    """
    notes_dir = "notes"
    
    # Сначала получаем все заметки
    note_files = []
    for filepath in sorted(glob.glob(os.path.join(notes_dir, "*.md"))):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Извлекаем title из frontmatter или имени файла
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
            
            note_files.append(f"{title}\t{filepath}")
            
        except Exception as e:
            print(f"Error reading {filepath}: {e}", file=sys.stderr)
    
    if not note_files:
        print("No notes found.", file=sys.stderr)
        return
    
    # Формируем команду fzf
    fzf_cmd = ['fzf', '--prompt', 'Search Notes > ', '--height', '40%', '--reverse', '--border']
    
    if tag:
        clean_tag = tag.lstrip('#')
        # Фильтруем заметки по тегу
        filtered_notes = []
        for filepath in glob.glob(os.path.join(notes_dir, "*.md")):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if content.startswith('---\n'):
                    second_delimiter = content.find('\n---\n', 4)
                    if second_delimiter != -1:
                        frontmatter = content[4:second_delimiter]
                        try:
                            data = yaml.safe_load(frontmatter)
                            if data and 'tags' in data:
                                if clean_tag in data['tags']:
                                    title = data.get('title', os.path.basename(filepath).replace('.md', ''))
                                    filtered_notes.append(f"{title}\t{filepath}")
                        except yaml.YAMLError:
                            continue
            except Exception:
                continue
        note_files = filtered_notes
    
    # Запускаем fzf
    try:
        result = subprocess.run(fzf_cmd, input='\n'.join(note_files), text=True, capture_output=True)
        
        if result.returncode == 0 and result.stdout.strip():
            selected = result.stdout.strip()
            # Извлекаем путь
            filepath = selected.split('\t')[-1]
            print(f"Opening: {filepath}")
            # Открытие в редакторе (настраивается)
            editor = os.getenv('EDITOR', 'code')
            subprocess.run([editor, filepath])
        elif result.returncode == 1:
            print("No selection made.", file=sys.stderr)
        elif result.returncode == 130:
            print("Search cancelled.", file=sys.stderr)
        
    except FileNotFoundError:
        print("fzf not found. Please install fzf from https://github.com/junegunn/fzf", file=sys.stderr)
    except Exception as e:
        print(f"Error running fzf: {e}", file=sys.stderr)

def open_note(note_id: str, editor_cmd: str = "code"):
    """
    Open a note by ID for editing.
    
    Args:
        note_id: The ID of the note (filename without extension)
        editor_cmd: Command to open the editor (default: "code")
    """
    notes_dir = "notes"
    filepath = os.path.join(notes_dir, f"{note_id}.md")
    
    if os.path.exists(filepath):
        print(f"Opening note: {filepath}")
        try:
            subprocess.run([editor_cmd, filepath])
        except Exception as e:
            print(f"Failed to open editor {editor_cmd}: {e}", file=sys.stderr)
    else:
        print(f"Note {note_id} not found.", file=sys.stderr)
    """
    Interactive search using fzf.
    
    Args:
        tag: Optional tag to filter notes
    """
    notes_dir = "notes"
    
    # Сначала получаем все заметки
    note_files = []
    for filepath in sorted(glob.glob(os.path.join(notes_dir, "*.md"))):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Извлекаем title из frontmatter или имени файла
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
            
            note_files.append(f"{title}\t{filepath}")
            
        except Exception as e:
            print(f"Error reading {filepath}: {e}", file=sys.stderr)
    
    if not note_files:
        print("No notes found.", file=sys.stderr)
        return
    
    # Формируем команду fzf
    fzf_cmd = ['fzf', '--prompt', 'Search Notes > ', '--height', '40%', '--reverse', '--border']
    
    if tag:
        clean_tag = tag.lstrip('#')
        # Фильтруем заметки по тегу
        filtered_notes = []
        for filepath in glob.glob(os.path.join(notes_dir, "*.md")):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if content.startswith('---\n'):
                    second_delimiter = content.find('\n---\n', 4)
                    if second_delimiter != -1:
                        frontmatter = content[4:second_delimiter]
                        try:
                            data = yaml.safe_load(frontmatter)
                            if data and 'tags' in data:
                                if clean_tag in data['tags']:
                                    title = data.get('title', os.path.basename(filepath).replace('.md', ''))
                                    filtered_notes.append(f"{title}\t{filepath}")
                        except yaml.YAMLError:
                            continue
            except Exception:
                continue
        note_files = filtered_notes
    
    # Запускаем fzf
    try:
        result = subprocess.run(fzf_cmd, input='\n'.join(note_files), text=True, capture_output=True)
        
        if result.returncode == 0 and result.stdout.strip():
            selected = result.stdout.strip()
            # Извлекаем путь
            filepath = selected.split('\t')[-1]
            print(f"Opening: {filepath}")
            # Открытие в редакторе (настраивается)
            editor = os.getenv('EDITOR', 'code')
            subprocess.run([editor, filepath])
        elif result.returncode == 1:
            print("No selection made.", file=sys.stderr)
        elif result.returncode == 130:
            print("Search cancelled.", file=sys.stderr)
        
    except FileNotFoundError:
        print("fzf not found. Please install fzf from https://github.com/junegunn/fzf", file=sys.stderr)
    except Exception as e:
        print(f"Error running fzf: {e}", file=sys.stderr)