import os
import datetime
import yaml

def save_note(content, tags, title=None):
    # Ensure notes directory exists
    notes_dir = "notes"
    os.makedirs(notes_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.datetime.now()
    filename = timestamp.strftime("%Y%m%d%H%M")
    # Use title to create filename, make it URL-friendly
    if title:
        safe_title = title.strip().replace(' ', '-').replace('_', '-').lower()
        filename = f"{filename}-{safe_title}.md"
    else:
        filename = f"{filename}-untitled.md"
    
    filepath = os.path.join(notes_dir, filename)
    
    # Create note content with YAML frontmatter
    note_data = {
        'title': title or 'Untitled Note',
        'date': timestamp.isoformat(),
        'tags': tags
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('---\n')
        yaml.dump(note_data, f, allow_unicode=True)
        f.write('---\n\n')
        f.write(content)
    
    return filepath