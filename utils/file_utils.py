import os
import base64
import tempfile
from pathlib import Path

def create_download_link(content, filename, link_text):
    """
    Create a download link for text content
    """
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

def save_to_project_folder(content, filename, folder_path):
    """
    Save content to a file in the project folder
    Returns the full path to the saved file
    """
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, filename)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return file_path

def get_file_extension(filename):
    """
    Get the file extension from a filename
    """
    return os.path.splitext(filename)[1].lower()

def is_text_file(filename):
    """
    Check if a file is likely to be a text file based on its extension
    """
    text_extensions = [
        '.txt', '.py', '.js', '.html', '.css', '.md', '.json', '.xml', 
        '.csv', '.c', '.cpp', '.h', '.java', '.php', '.rb', '.go', 
        '.rs', '.ts', '.sh', '.bat', '.ps1', '.yaml', '.yml', 
        '.toml', '.ini', '.cfg'
    ]
    
    ext = get_file_extension(filename)
    return ext in text_extensions

def get_common_filename(left_filename, right_filename):
    """
    Generate a common filename for the reconciled output
    """
    left_name = Path(left_filename).stem
    right_name = Path(right_filename).stem
    ext = Path(left_filename).suffix
    
    if left_name == right_name:
        return f"{left_name}_reconciled{ext}"
    else:
        return f"{left_name}_{right_name}_reconciled{ext}"
