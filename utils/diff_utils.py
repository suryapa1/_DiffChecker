import difflib
import pygments
from pygments import lexers
from pygments.formatters import HtmlFormatter
import re
import html

def get_diff_lines(left_text, right_text):
    """
    Generate line-by-line diff between two text files.
    Returns a list of tuples (tag, left_line, right_line, left_line_num, right_line_num)
    where tag is one of 'equal', 'replace', 'delete', 'insert'
    """
    left_lines = left_text.splitlines()
    right_lines = right_text.splitlines()
    
    # Generate diff using difflib
    differ = difflib.Differ()
    diff = list(differ.compare(left_lines, right_lines))
    
    # Process diff to create a more structured representation
    result = []
    left_line_num = 0
    right_line_num = 0
    
    for line in diff:
        tag = line[0]
        content = line[2:]
        
        if tag == ' ':  # Equal lines
            result.append(('equal', content, content, left_line_num, right_line_num))
            left_line_num += 1
            right_line_num += 1
        elif tag == '-':  # Line only in left file
            result.append(('delete', content, '', left_line_num, None))
            left_line_num += 1
        elif tag == '+':  # Line only in right file
            result.append(('insert', '', content, None, right_line_num))
            right_line_num += 1
        elif tag == '?':  # Hint line, skip
            continue
    
    return result

def highlight_code(code, filename):
    """
    Apply syntax highlighting to code based on file extension.
    Returns HTML with syntax highlighting.
    """
    try:
        # Try to guess lexer from filename
        lexer = pygments.lexers.get_lexer_for_filename(filename)
    except pygments.util.ClassNotFound:
        # Fallback to text lexer
        lexer = pygments.lexers.TextLexer()
    
    formatter = HtmlFormatter(style='colorful')
    highlighted = pygments.highlight(code, lexer, formatter)
    
    return highlighted

def generate_diff_html(diff_lines, left_filename, right_filename):
    """
    Generate HTML representation of diff with syntax highlighting.
    """
    # Get CSS for syntax highlighting
    css = HtmlFormatter(style='colorful').get_style_defs('.highlight')
    
    # Start building HTML
    html_output = f"""
    <style>
        {css}
        .diff-container {{
            display: flex;
            font-family: monospace;
            width: 100%;
        }}
        .line-numbers {{
            text-align: right;
            padding-right: 10px;
            color: #999;
            user-select: none;
        }}
        .diff-content {{
            flex-grow: 1;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .diff-line {{
            display: flex;
            width: 100%;
        }}
        .equal {{
            background-color: #f8f8f8;
        }}
        .delete {{
            background-color: #ffdddd;
        }}
        .insert {{
            background-color: #ddffdd;
        }}
        .replace {{
            background-color: #f8f0dd;
        }}
        .diff-side {{
            width: 50%;
            border-right: 1px solid #ccc;
            padding: 0 5px;
        }}
    </style>
    <div class="diff-container">
    """
    
    # Left side
    html_output += '<div class="diff-side">'
    html_output += f'<h4>{html.escape(left_filename)}</h4>'
    
    for tag, left_line, _, left_line_num, _ in diff_lines:
        if left_line_num is not None:
            line_class = tag
            html_output += f'<div class="diff-line {line_class}">'
            html_output += f'<div class="line-numbers">{left_line_num + 1}</div>'
            html_output += f'<div class="diff-content">{html.escape(left_line)}</div>'
            html_output += '</div>'
    
    html_output += '</div>'
    
    # Right side
    html_output += '<div class="diff-side">'
    html_output += f'<h4>{html.escape(right_filename)}</h4>'
    
    for tag, _, right_line, _, right_line_num in diff_lines:
        if right_line_num is not None:
            line_class = tag
            html_output += f'<div class="diff-line {line_class}">'
            html_output += f'<div class="line-numbers">{right_line_num + 1}</div>'
            html_output += f'<div class="diff-content">{html.escape(right_line)}</div>'
            html_output += '</div>'
    
    html_output += '</div>'
    html_output += '</div>'
    
    return html_output

def apply_changes(source_text, target_text, direction):
    """
    Apply changes from source to target based on direction.
    direction: 'left_to_right' or 'right_to_left'
    Returns the reconciled text.
    """
    source_lines = source_text.splitlines()
    target_lines = target_text.splitlines()
    
    if direction == 'left_to_right':
        # Apply left changes to right
        return '\n'.join(source_lines)
    else:
        # Apply right changes to left
        return '\n'.join(target_lines)

def apply_selective_changes(left_text, right_text, selected_lines, direction):
    """
    Apply only selected line changes from source to target.
    selected_lines: List of line numbers to apply
    direction: 'left_to_right' or 'right_to_left'
    Returns the reconciled text.
    """
    left_lines = left_text.splitlines()
    right_lines = right_text.splitlines()
    
    # Generate diff
    diff_lines = get_diff_lines(left_text, right_text)
    
    # Create new reconciled text based on selected changes
    if direction == 'left_to_right':
        # Start with right text
        result_lines = right_lines.copy()
        
        # Apply selected changes from left to right
        for line_num in selected_lines:
            for tag, left_line, _, left_line_num, right_line_num in diff_lines:
                if left_line_num == line_num:
                    if right_line_num is not None:
                        # Replace line in right
                        result_lines[right_line_num] = left_line
                    else:
                        # Insert line from left (this is more complex and requires adjusting indices)
                        # For simplicity, we'll just use the full left text in this case
                        return '\n'.join(left_lines)
    else:
        # Start with left text
        result_lines = left_lines.copy()
        
        # Apply selected changes from right to left
        for line_num in selected_lines:
            for tag, _, right_line, left_line_num, right_line_num in diff_lines:
                if right_line_num == line_num:
                    if left_line_num is not None:
                        # Replace line in left
                        result_lines[left_line_num] = right_line
                    else:
                        # Insert line from right (this is more complex and requires adjusting indices)
                        # For simplicity, we'll just use the full right text in this case
                        return '\n'.join(right_lines)
    
    return '\n'.join(result_lines)
