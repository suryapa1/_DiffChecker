import os
import tempfile

# Create test files for validation
def create_test_files():
    """
    Create various test files for validating the diff checker application
    """
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_files")
    os.makedirs(test_dir, exist_ok=True)
    
    # Test case 1: Simple text files with minor differences
    with open(os.path.join(test_dir, "text_file1.txt"), "w") as f:
        f.write("""This is a simple text file.
It has multiple lines.
This line will be different.
This line is the same in both files.
Another line that will be different.
Final line is the same.""")
    
    with open(os.path.join(test_dir, "text_file2.txt"), "w") as f:
        f.write("""This is a simple text file.
It has multiple lines.
This line has been changed in the second file.
This line is the same in both files.
This is a completely new line that doesn't exist in the first file.
Final line is the same.""")
    
    # Test case 2: Python code files with syntax differences
    with open(os.path.join(test_dir, "code_file1.py"), "w") as f:
        f.write("""def calculate_sum(a, b):
    # This function calculates the sum of two numbers
    return a + b

def calculate_difference(a, b):
    # This function calculates the difference between two numbers
    return a - b

# Main function
def main():
    x = 10
    y = 5
    print(f"Sum: {calculate_sum(x, y)}")
    print(f"Difference: {calculate_difference(x, y)}")

if __name__ == "__main__":
    main()
""")
    
    with open(os.path.join(test_dir, "code_file2.py"), "w") as f:
        f.write("""def calculate_sum(a, b):
    # This function calculates the sum of two numbers
    return a + b

def calculate_difference(a, b):
    # This function calculates the difference between two numbers
    return a - b
    
def calculate_product(a, b):
    # This function calculates the product of two numbers
    return a * b

# Main function
def main():
    x = 10
    y = 5
    print(f"Sum: {calculate_sum(x, y)}")
    print(f"Difference: {calculate_difference(x, y)}")
    print(f"Product: {calculate_product(x, y)}")

if __name__ == "__main__":
    main()
""")
    
    # Test case 3: HTML files with structure differences
    with open(os.path.join(test_dir, "webpage1.html"), "w") as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        h1 {
            color: blue;
        }
    </style>
</head>
<body>
    <h1>Welcome to the Test Page</h1>
    <p>This is a paragraph of text.</p>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
        <li>Item 3</li>
    </ul>
    <footer>
        <p>Copyright 2025</p>
    </footer>
</body>
</html>
""")
    
    with open(os.path.join(test_dir, "webpage2.html"), "w") as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f0f0f0;
        }
        h1 {
            color: green;
        }
    </style>
</head>
<body>
    <h1>Welcome to the Updated Test Page</h1>
    <p>This is a paragraph of text with some changes.</p>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
        <li>Item 3</li>
        <li>Item 4</li>
    </ul>
    <div class="new-section">
        <h2>New Section</h2>
        <p>This section doesn't exist in the original file.</p>
    </div>
    <footer>
        <p>Copyright 2025 - All Rights Reserved</p>
    </footer>
</body>
</html>
""")
    
    # Create a zip file with multiple files for folder testing
    import zipfile
    zip_path = os.path.join(test_dir, "test_folder.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(os.path.join(test_dir, "text_file1.txt"), arcname="text_file1.txt")
        zipf.write(os.path.join(test_dir, "code_file1.py"), arcname="code_file1.py")
        zipf.write(os.path.join(test_dir, "webpage1.html"), arcname="webpage1.html")
    
    zip_path2 = os.path.join(test_dir, "test_folder2.zip")
    with zipfile.ZipFile(zip_path2, 'w') as zipf:
        zipf.write(os.path.join(test_dir, "text_file2.txt"), arcname="text_file1.txt")
        zipf.write(os.path.join(test_dir, "code_file2.py"), arcname="code_file1.py")
        zipf.write(os.path.join(test_dir, "webpage2.html"), arcname="webpage1.html")
    
    return test_dir

if __name__ == "__main__":
    test_dir = create_test_files()
    print(f"Test files created in: {test_dir}")
