import streamlit as st
import os
import tempfile
import shutil
import zipfile
import difflib
import base64
from pathlib import Path

# Import utility modules
from utils.diff_utils import get_diff_lines, highlight_code, generate_diff_html, apply_changes, apply_selective_changes
from utils.file_utils import create_download_link, save_to_project_folder, get_file_extension, is_text_file, get_common_filename
from utils.document_utils import extract_text_from_file, process_zip_file, is_binary_file, is_resume
from utils.resume_utils import compare_resume_sections, generate_resume_diff_html, compare_resume_skills, generate_skills_comparison_html

# Set page configuration
st.set_page_config(
    page_title="Diff Checker",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton button {
        width: 100%;
    }
    .diff-viewer {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 20px;
        max-height: 600px;
        overflow-y: auto;
    }
    .file-selector {
        margin-bottom: 20px;
    }
    .reconcile-controls {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .resume-diff {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Create output directory if it doesn't exist
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize session state
if 'left_files' not in st.session_state:
    st.session_state.left_files = {}
if 'right_files' not in st.session_state:
    st.session_state.right_files = {}
if 'left_selected_file' not in st.session_state:
    st.session_state.left_selected_file = None
if 'right_selected_file' not in st.session_state:
    st.session_state.right_selected_file = None
if 'temp_dir' not in st.session_state:
    st.session_state.temp_dir = tempfile.mkdtemp()
if 'reconciled_text' not in st.session_state:
    st.session_state.reconciled_text = None
if 'selected_lines' not in st.session_state:
    st.session_state.selected_lines = []
if 'diff_lines' not in st.session_state:
    st.session_state.diff_lines = []
if 'is_resume_comparison' not in st.session_state:
    st.session_state.is_resume_comparison = False

# Function to handle individual file upload
def handle_file_upload(uploaded_file, target_dict, file_key):
    if uploaded_file is not None:
        content = uploaded_file.getvalue()
        
        # Check if it's a ZIP file
        if uploaded_file.name.lower().endswith('.zip'):
            target_dict = process_zip_file(content, target_dict)
            return target_dict, list(target_dict.keys())[0] if target_dict else None
        
        # Extract text from the file
        extracted_text = extract_text_from_file(content, uploaded_file.name)
        if extracted_text is not None:
            target_dict[uploaded_file.name] = extracted_text
            return target_dict, uploaded_file.name
        else:
            st.error(f"File {uploaded_file.name} appears to be binary or unsupported. Only text and Office documents are supported.")
            return target_dict, None
    return target_dict, None

# Function to toggle line selection for selective reconciliation
def toggle_line_selection(line_num):
    if line_num in st.session_state.selected_lines:
        st.session_state.selected_lines.remove(line_num)
    else:
        st.session_state.selected_lines.append(line_num)

# Main app title
st.title("Diff Checker")
st.markdown("Upload files or folders to compare, edit, and reconcile differences.")

# Create two columns for left and right panes
left_col, right_col = st.columns(2)

# Left pane
with left_col:
    st.header("Left Side")
    left_upload_type = st.radio("Upload type (Left):", ["File", "Folder (ZIP)"], key="left_upload_type")
    
    if left_upload_type == "File":
        left_file = st.file_uploader("Upload a file (Left)", key="left_file")
        if left_file is not None:
            st.session_state.left_files, selected = handle_file_upload(left_file, st.session_state.left_files, "left")
            if selected:
                st.session_state.left_selected_file = selected
    else:
        left_zip = st.file_uploader("Upload a ZIP folder (Left)", type="zip", key="left_zip")
        if left_zip is not None:
            st.session_state.left_files = process_zip_file(left_zip.getvalue(), st.session_state.left_files)
            if st.session_state.left_files:
                st.session_state.left_selected_file = list(st.session_state.left_files.keys())[0]
    
    # Display file list for left side
    if st.session_state.left_files:
        st.subheader("Files")
        left_selected = st.selectbox(
            "Select a file (Left)", 
            options=list(st.session_state.left_files.keys()),
            index=list(st.session_state.left_files.keys()).index(st.session_state.left_selected_file) if st.session_state.left_selected_file in st.session_state.left_files else 0,
            key="left_file_select"
        )
        st.session_state.left_selected_file = left_selected

# Right pane
with right_col:
    st.header("Right Side")
    right_upload_type = st.radio("Upload type (Right):", ["File", "Folder (ZIP)"], key="right_upload_type")
    
    if right_upload_type == "File":
        right_file = st.file_uploader("Upload a file (Right)", key="right_file")
        if right_file is not None:
            st.session_state.right_files, selected = handle_file_upload(right_file, st.session_state.right_files, "right")
            if selected:
                st.session_state.right_selected_file = selected
    else:
        right_zip = st.file_uploader("Upload a ZIP folder (Right)", type="zip", key="right_zip")
        if right_zip is not None:
            st.session_state.right_files = process_zip_file(right_zip.getvalue(), st.session_state.right_files)
            if st.session_state.right_files:
                st.session_state.right_selected_file = list(st.session_state.right_files.keys())[0]
    
    # Display file list for right side
    if st.session_state.right_files:
        st.subheader("Files")
        right_selected = st.selectbox(
            "Select a file (Right)", 
            options=list(st.session_state.right_files.keys()),
            index=list(st.session_state.right_files.keys()).index(st.session_state.right_selected_file) if st.session_state.right_selected_file in st.session_state.right_files else 0,
            key="right_file_select"
        )
        st.session_state.right_selected_file = right_selected

# Display upload status
st.sidebar.subheader("Upload Status")
st.sidebar.info(f"Left files: {len(st.session_state.left_files)}")
st.sidebar.info(f"Right files: {len(st.session_state.right_files)}")

# Clear uploads button
if st.sidebar.button("Clear All Uploads"):
    st.session_state.left_files = {}
    st.session_state.right_files = {}
    st.session_state.left_selected_file = None
    st.session_state.right_selected_file = None
    st.session_state.reconciled_text = None
    st.session_state.selected_lines = []
    st.session_state.diff_lines = []
    st.session_state.is_resume_comparison = False
    st.experimental_rerun()

# Diff preview and editing
st.markdown("---")
st.subheader("Diff Preview and Editing")

# Check if files are selected on both sides
if st.session_state.left_selected_file and st.session_state.right_selected_file:
    left_text = st.session_state.left_files[st.session_state.left_selected_file]
    right_text = st.session_state.right_files[st.session_state.right_selected_file]
    
    # Check if both files are resumes
    left_is_resume = is_resume(st.session_state.left_selected_file, left_text)
    right_is_resume = is_resume(st.session_state.right_selected_file, right_text)
    st.session_state.is_resume_comparison = left_is_resume and right_is_resume
    
    # Display comparison type
    if st.session_state.is_resume_comparison:
        st.info("Resume comparison mode activated. Specialized resume comparison features are enabled.")
    
    # Generate diff
    st.session_state.diff_lines = get_diff_lines(left_text, right_text)
    
    # Display diff statistics
    equal_lines = sum(1 for tag, _, _, _, _ in st.session_state.diff_lines if tag == 'equal')
    diff_lines = len(st.session_state.diff_lines) - equal_lines
    
    st.write(f"Comparing: **{st.session_state.left_selected_file}** and **{st.session_state.right_selected_file}**")
    st.write(f"Found {diff_lines} differences out of {len(st.session_state.diff_lines)} total lines.")
    
    # Diff controls
    st.markdown("### Reconciliation Controls")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Apply Left to Right (All)"):
            st.session_state.reconciled_text = apply_changes(left_text, right_text, 'left_to_right')
            st.success("Applied all changes from left to right")
    
    with col2:
        if st.button("Apply Right to Left (All)"):
            st.session_state.reconciled_text = apply_changes(left_text, right_text, 'right_to_left')
            st.success("Applied all changes from right to left")
    
    with col3:
        if st.button("Apply Selected Changes"):
            if st.session_state.selected_lines:
                # Determine direction based on which side has more selected lines
                left_selected = sum(1 for line_num in st.session_state.selected_lines if any(line_num == left_line_num for _, _, _, left_line_num, _ in st.session_state.diff_lines))
                right_selected = sum(1 for line_num in st.session_state.selected_lines if any(line_num == right_line_num for _, _, _, _, right_line_num in st.session_state.diff_lines))
                
                direction = 'left_to_right' if left_selected >= right_selected else 'right_to_left'
                st.session_state.reconciled_text = apply_selective_changes(left_text, right_text, st.session_state.selected_lines, direction)
                st.success(f"Applied selected changes ({direction.replace('_', ' ')})")
            else:
                st.warning("No lines selected for reconciliation")
    
    # Generate HTML diff view
    diff_html = generate_diff_html(st.session_state.diff_lines, st.session_state.left_selected_file, st.session_state.right_selected_file)
    
    # Display diff
    st.markdown("### Diff View")
    st.markdown("Click on lines to select them for selective reconciliation.")
    st.markdown('<div class="diff-viewer">' + diff_html + '</div>', unsafe_allow_html=True)
    
    # JavaScript for line selection
    st.markdown("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const diffLines = document.querySelectorAll('.diff-line');
        diffLines.forEach(line => {
            line.addEventListener('click', function() {
                this.classList.toggle('selected');
                const lineNum = this.querySelector('.line-numbers').textContent;
                // Use Streamlit's setComponentValue when available
            });
        });
    });
    </script>
    """, unsafe_allow_html=True)
    
    # Resume-specific comparison if both files are resumes
    if st.session_state.is_resume_comparison:
        st.markdown("---")
        st.subheader("Resume Comparison")
        
        # Compare resume sections
        section_comparisons = compare_resume_sections(left_text, right_text)
        resume_diff_html = generate_resume_diff_html(section_comparisons, st.session_state.left_selected_file, st.session_state.right_selected_file)
        
        # Compare skills
        skills_comparison = compare_resume_skills(left_text, right_text)
        skills_html = generate_skills_comparison_html(skills_comparison)
        
        # Display resume comparison
        st.markdown('<div class="resume-diff">' + resume_diff_html + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="resume-diff">' + skills_html + '</div>', unsafe_allow_html=True)
    
    # Reconciliation and output
    st.markdown("---")
    st.subheader("Reconciliation and Output")
    
    if st.session_state.reconciled_text:
        st.markdown("### Reconciled Text Preview")
        st.text_area("Preview", st.session_state.reconciled_text, height=200)
        
        # Generate output filename
        output_filename = get_common_filename(st.session_state.left_selected_file, st.session_state.right_selected_file)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Download button
            download_link = create_download_link(st.session_state.reconciled_text, output_filename, "Download Reconciled File")
            st.markdown(download_link, unsafe_allow_html=True)
        
        with col2:
            # Save to project button
            if st.button("Save to Project Folder"):
                saved_path = save_to_project_folder(st.session_state.reconciled_text, output_filename, OUTPUT_DIR)
                st.success(f"Saved to: {saved_path}")
    else:
        st.info("Use the reconciliation controls above to generate a reconciled output.")
else:
    st.info("Please upload and select files on both sides to view and edit differences.")

# Footer
st.markdown("---")
st.markdown("Diff Checker App - Built with Streamlit")
