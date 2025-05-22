# Enhanced Diff Checker Application - User Guide

## Overview

The Enhanced Diff Checker is a powerful application for comparing various document types, including text files, code files, Microsoft Office documents, and resumes. It allows you to upload files or folders, view differences, make changes in either direction, and generate reconciled output files.

## New Features

This enhanced version includes several major improvements:

- **Microsoft Office Support**: Compare Word documents (.docx), PowerPoint presentations (.pptx), and PDF files
- **Resume Comparison**: Specialized features for comparing resumes, including section-by-section comparison and skills analysis
- **Improved ZIP Handling**: Support for ZIP files with recursive extraction of nested archives
- **Binary File Filtering**: Automatic detection and filtering of binary or unsupported file formats
- **Enhanced Diff Visualization**: Better visualization of differences with syntax highlighting and interactive selection

## Installation and Setup

1. Ensure you have Python 3.6+ installed on your system
2. Clone or download the application files
3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Run the application:

```bash
streamlit run app.py
```

## Usage Guide

### 1. Uploading Files

- **Individual Files**: Select "File" from the radio buttons and use the file uploader
- **Folders**: Select "Folder (ZIP)" and upload a ZIP file containing multiple files
- Files will appear in the file selector dropdown once uploaded
- Supported formats include text files, code files, Word documents, PowerPoint presentations, and PDFs

### 2. Comparing Files

- Select files from both the left and right panes
- The diff view will automatically display differences between the selected files
- Differences are color-coded:
  - Green: Lines only in the right file
  - Red: Lines only in the left file
  - Yellow: Modified lines

### 3. Resume Comparison

When comparing resumes, the application automatically detects resume content and activates specialized comparison features:

- **Section-by-Section Comparison**: Compares common resume sections like Experience, Education, and Skills
- **Skills Analysis**: Identifies common skills and skills unique to each resume
- **Visual Highlighting**: Color-coded visualization of differences between resume sections

### 4. Reconciling Differences

- **Apply All Changes**: Use the "Apply Left to Right" or "Apply Right to Left" buttons to apply all changes
- **Selective Changes**: Click on specific lines in the diff view to select them, then use "Apply Selected Changes"
- The reconciled text will appear in the preview area below

### 5. Saving and Downloading

- **Download**: Click the "Download Reconciled File" link to download the reconciled file
- **Save to Project**: Click "Save to Project Folder" to save the file to the application's output directory

## File Types Supported

The application now supports a wide range of file types:

- Plain text files (.txt)
- Code files (.py, .js, .html, .css, etc.)
- Microsoft Word documents (.docx)
- PDF files (.pdf)
- PowerPoint presentations (.pptx)
- ZIP archives (with recursive extraction)

Binary files and unsupported formats are automatically filtered out during upload.

## Tips for Resume Comparison

- For best results, ensure resumes have clear section headers (Experience, Education, Skills, etc.)
- The skills comparison works best with technical and professional skills that match common industry terminology
- When comparing multiple resumes, use the ZIP upload feature to process them in batches

## Project Structure

```
streamlit_diff_checker/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Project dependencies
├── utils/
│   ├── __init__.py
│   ├── diff_utils.py       # Diff generation and processing
│   ├── file_utils.py       # File handling utilities
│   ├── document_utils.py   # Office document processing
│   └── resume_utils.py     # Resume comparison features
├── output/                 # Directory for saved reconciled files
└── test_files/             # Sample files for testing
```

## Troubleshooting

- If a file fails to upload, check if it's in a supported format
- For large ZIP files, the processing may take a moment
- If Office document extraction fails, ensure the document is not password-protected
- For resume comparison, ensure the resumes have standard section headers for best results
# _DiffChecker
