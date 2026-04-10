import os
from pathlib import Path
from typing import List, Set

def get_note_suggestions() -> Set[str]:
    """Get all available note filenames (stems) from the notes directory."""
    notes_dir = Path("notes")
    if not notes_dir.exists():
        return set()
    
    suggestions = set()
    for file_path in notes_dir.glob("*.md"):
        suggestions.add(file_path.stem)
    return suggestions

def should_trigger_autocomplete(content: str, cursor_pos: int) -> bool:
    """Check if autocomplete should be triggered at current position."""
    if cursor_pos < 2:
        return False
    
    # Look at the two characters before cursor
    prefix = content[max(0, cursor_pos-2):cursor_pos]
    return prefix == "[["

def find_current_link_prefix(content: str, cursor_pos: int) -> str:
    """Find the current link text being typed after [[."""
    # Start from cursor and go backward to find the [[
    start = content.rfind("[[", 0, cursor_pos)
    if start == -1:
        return ""
    
    # Extract everything between [[ and cursor
    return content[start+2:cursor_pos]

def filter_suggestions(suggestions: Set[str], prefix: str) -> List[str]:
    """Filter suggestions based on current input prefix."""
    if not prefix.strip():
        return sorted(suggestions)
    
    prefix_lower = prefix.lower()
    filtered = [s for s in suggestions if prefix_lower in s.lower()]
    return sorted(filtered)

def format_suggestions_for_editor(suggestions: List[str], max_suggestions: int = 10) -> str:
    """Format suggestions as a comment block for the editor."""
    if not suggestions:
        return ""
    
    # Take only top N suggestions
    limited = suggestions[:max_suggestions]
    
    lines = ["<!-- Autocomplete suggestions -->"]
    for i, suggestion in enumerate(limited, 1):
        lines.append(f"<!-- {i}. {suggestion} -->")
    
    if len(suggestions) > max_suggestions:
        lines.append(f"<!-- ... and {len(suggestions) - max_suggestions} more -->")
    
    lines.append("<!-- End of suggestions -->\n")
    return "\n".join(lines)

def insert_suggestions(content: str, suggestions_text: str) -> str:
    """Insert suggestions at the end of the file, ensuring proper spacing."""
    # Remove any existing suggestion block
    lines = content.split('\n')
    
    # Find the start of existing suggestions
    suggestion_start = -1
    for i, line in enumerate(lines):
        if "<!-- Autocomplete suggestions -->" in line:
            suggestion_start = i
            break
    
    # If found, remove from that point onward
    if suggestion_start != -1:
        lines = lines[:suggestion_start]
    
    # Remove trailing whitespace/empty lines
    while lines and not lines[-1].strip():
        lines.pop()
    
    # Add suggestions with spacing
    if lines:
        lines.append("")
    lines.append(suggestions_text)
    
    return '\n'.join(lines)

def process_file_for_autocomplete(file_path: str):
    """Process a file to add autocomplete suggestions if needed."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get current cursor position from environment
        cursor_pos_str = os.getenv('ZETTEL_CURSOR_POS')
        cursor_pos = int(cursor_pos_str) if cursor_pos_str and cursor_pos_str.isdigit() else len(content)
        
        # Check if we should trigger autocomplete
        if not should_trigger_autocomplete(content, cursor_pos):
            return  # Don't modify file
        
        # Get current link prefix
        link_prefix = find_current_link_prefix(content, cursor_pos)
        
        # Get and filter suggestions
        all_suggestions = get_note_suggestions()
        filtered_suggestions = filter_suggestions(all_suggestions, link_prefix)
        
        # Format suggestions
        suggestions_text = format_suggestions_for_editor(filtered_suggestions)
        
        # Only modify file if we have suggestions
        if not suggestions_text.strip():
            return
        
        # Insert suggestions into file
        new_content = insert_suggestions(content, suggestions_text)
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
    except (IOError, OSError):
        # Fail silently to avoid disrupting the user's editing experience
        pass

def remove_suggestions(file_path: str):
    """Remove autocomplete suggestions from a file before saving."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Find the start of suggestions
        suggestion_start = -1
        for i, line in enumerate(lines):
            if "<!-- Autocomplete suggestions -->" in line:
                suggestion_start = i
                break
        
        # If found, remove from that point onward
        if suggestion_start != -1:
            lines = lines[:suggestion_start]
            
            # Remove trailing whitespace/empty lines
            while lines and not lines[-1].strip():
                lines.pop()
            
            # Add single newline at end
            if lines:
                lines.append("")
            
            # Write back to file
            new_content = '\n'.join(lines)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
    except (IOError, OSError):
        # Fail silently
        pass