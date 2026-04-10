import os
import glob
from typing import List


def get_note_suggestions(notes_dir: str = "notes/") -> List[str]:
    """
    Scan the notes directory for .md files and return a list of note titles.
    
    Args:
        notes_dir (str): Path to the notes directory
    
    Returns:
        List[str]: List of note filenames without .md extension
    """
    try:
        if not os.path.exists(notes_dir):
            print(f"Notes directory {notes_dir} does not exist")
            return []
        
        # Use glob to find all .md files in the notes directory
        pattern = os.path.join(notes_dir, "*.md")
        md_files = glob.glob(pattern)
        
        # Extract filenames without the .md extension
        suggestions = []
        for file_path in md_files:
            filename = os.path.basename(file_path)
            title = os.path.splitext(filename)[0]
            suggestions.append(title)
            
        return suggestions
        
    except Exception as e:
        print(f"Error scanning notes directory: {e}")
        return []


def create_note_if_not_exists(title: str) -> bool:
    """
    Create a new empty note with the given title if it doesn't exist.
    
    Args:
        title (str): Title of the note to create
    
    Returns:
        bool: True if note was created or already exists, False otherwise
    """
    try:
        # Check if note with this title already exists
        existing_notes = get_note_suggestions()
        if title in existing_notes:
            return True
            
        # Create empty note using storage function
        from core.storage import save_note
        filepath = save_note(content="", tags=[], title=title)
        print(f"Created new note: {title}")
        return True
        
    except Exception as e:
        print(f"Error creating note {title}: {e}")
        return False


def process_file_for_autocomplete(filepath: str) -> bool:
    """
    Read the content of the file and insert HTML comments with note suggestions
    when [[ is detected. If a referenced note doesn't exist, prompt to create it.
    
    Args:
        filepath (str): Path to the file to process
    
    Returns:
        bool: True if file was processed successfully, False otherwise
    """
    try:
        # Read the file content
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()

        # Get note suggestions
        suggestions = get_note_suggestions()
        
        # Extract all [[note]] references
        import re
        pattern = r'\[\[(.*?)\]\]'
        matches = re.findall(pattern, content)
        
        # Check for non-existent notes and prompt to create
        for match in matches:
            note_title = match.strip()
            if note_title and note_title not in suggestions:
                user_input = input(f"Note '{note_title}' does not exist. Create it? (y/N): ")
                if user_input.lower() == 'y':
                    create_note_if_not_exists(note_title)
                    # Refresh suggestions after creating new note
                    suggestions = get_note_suggestions()
        
        # Only proceed with autocomplete if we have suggestions
        if not suggestions:
            return True
            
        # Create suggestions HTML comment with newlines for better readability
        suggestions_str = ", ".join(suggestions)
        suggestions_comment = f"\n<!-- SUGGESTIONS: {suggestions_str} -->\n"
        
        # Find all [[ and add suggestions after each one
        # Only add suggestions if [[ is found and we have suggestions
        if '[[' in content:
            # Split content by '[[', process each part, then rejoin
            parts = content.split('[[')
            updated_parts = [parts[0]]  # First part before any [[
            
            # Add suggestions after each [[
            for part in parts[1:]:
                # Only add the suggestion comment if it's not already present in the part
                if '<!-- SUGGESTIONS:' not in part:
                    updated_parts.append(f'[[{suggestions_comment}{part}')
                else:
                    updated_parts.append(f'[[{part}')
                
            updated_content = ''.join(updated_parts)
            
            # Write the updated content back to the file
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(updated_content)
                
        return True
        
    except Exception as e:
        print(f"Error processing file for autocomplete: {e}")
        return False


def remove_suggestions(filepath: str) -> bool:
    """
    Remove all HTML comments containing suggestions from the file.
    
    Args:
        filepath (str): Path to the file to clean up
    
    Returns:
        bool: True if file was cleaned successfully, False otherwise
    """
    try:
        # Read the file content
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()

        # Remove suggestion comments
        # Look for <!-- SUGGESTIONS: ... --> pattern with optional newlines
        import re
        pattern = r'\n?<!-- SUGGESTIONS: .*? -->\n?'
        updated_content = re.sub(pattern, '', content)
        
        # Write the cleaned content back to the file
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(updated_content)
            
        return True
        
    except Exception as e:
        print(f"Error removing suggestions: {e}")
        return False