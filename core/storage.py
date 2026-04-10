import os
import datetime
import yaml

def save_note(content, tags):
    # Ensure notes directory exists
    notes_dir = "notes"
    os.makedirs(notes_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.datetime.now()
    filename = timestamp.strftime("%Y-%m-%d-%H%M%S.md")
    filepath = os.path.join(notes_dir, filename)
    
    # Create note content with YAML frontmatter
    note_data = {
        'date': timestamp.isoformat(),
        'tags': tags
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('---\n')
        yaml.dump(note_data, f, allow_unicode=True)
        f.write('---\n\n')
        f.write(content)