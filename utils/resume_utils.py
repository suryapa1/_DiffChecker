import re
import difflib
from collections import defaultdict

def extract_resume_sections(text):
    """
    Extract common sections from a resume text
    Returns a dictionary with section names as keys and content as values
    """
    # Common section headers in resumes
    section_patterns = [
        (r'(?i)(?:professional\s+)?summary|profile', 'summary'),
        (r'(?i)objective', 'objective'),
        (r'(?i)(?:work\s+|professional\s+)?experience|employment(?:\s+history)?', 'experience'),
        (r'(?i)education(?:al)?(?:\s+background)?', 'education'),
        (r'(?i)skills|technical\s+skills|core\s+competencies', 'skills'),
        (r'(?i)certifications?|licenses?', 'certifications'),
        (r'(?i)projects?', 'projects'),
        (r'(?i)publications?', 'publications'),
        (r'(?i)awards?|honors?|achievements?', 'awards'),
        (r'(?i)languages?', 'languages'),
        (r'(?i)references?', 'references'),
        (r'(?i)volunteer(?:ing)?|community(?:\s+service)?', 'volunteer')
    ]
    
    # Split text into lines
    lines = text.split('\n')
    
    # Initialize sections dictionary
    sections = defaultdict(str)
    current_section = 'other'
    
    # Process each line
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Check if this line is a section header
        section_found = False
        for pattern, section_name in section_patterns:
            if re.match(f'^{pattern}[:\s]*$', line, re.IGNORECASE):
                current_section = section_name
                section_found = True
                break
        
        if not section_found:
            # Add content to current section
            sections[current_section] += line + '\n'
    
    # Clean up sections
    for section in sections:
        sections[section] = sections[section].strip()
    
    return dict(sections)

def compare_resume_sections(left_text, right_text):
    """
    Compare two resumes section by section
    Returns a dictionary with section comparisons
    """
    # Extract sections from both resumes
    left_sections = extract_resume_sections(left_text)
    right_sections = extract_resume_sections(right_text)
    
    # Get all unique section names
    all_sections = set(list(left_sections.keys()) + list(right_sections.keys()))
    
    # Compare each section
    section_comparisons = {}
    for section in all_sections:
        left_content = left_sections.get(section, '')
        right_content = right_sections.get(section, '')
        
        if left_content and right_content:
            # Both resumes have this section, compare them
            differ = difflib.Differ()
            diff = list(differ.compare(left_content.splitlines(), right_content.splitlines()))
            section_comparisons[section] = {
                'left_only': False,
                'right_only': False,
                'diff': diff,
                'similarity': difflib.SequenceMatcher(None, left_content, right_content).ratio()
            }
        elif left_content:
            # Only left resume has this section
            section_comparisons[section] = {
                'left_only': True,
                'right_only': False,
                'diff': [f"- {line}" for line in left_content.splitlines()],
                'similarity': 0.0
            }
        else:
            # Only right resume has this section
            section_comparisons[section] = {
                'left_only': False,
                'right_only': True,
                'diff': [f"+ {line}" for line in right_content.splitlines()],
                'similarity': 0.0
            }
    
    return section_comparisons

def generate_resume_diff_html(section_comparisons, left_filename, right_filename):
    """
    Generate HTML representation of resume diff with section highlighting
    """
    # Start building HTML
    html_output = f"""
    <style>
        .resume-diff-container {{
            font-family: Arial, sans-serif;
            width: 100%;
        }}
        .section-header {{
            background-color: #f0f0f0;
            padding: 10px;
            margin-top: 20px;
            font-weight: bold;
            border-radius: 5px;
        }}
        .section-similarity {{
            float: right;
            color: #666;
        }}
        .section-content {{
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-top: 5px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .left-only {{
            background-color: #ffdddd;
        }}
        .right-only {{
            background-color: #ddffdd;
        }}
        .diff-line {{
            margin: 0;
            padding: 2px 0;
        }}
        .diff-added {{
            background-color: #ddffdd;
        }}
        .diff-removed {{
            background-color: #ffdddd;
        }}
        .diff-unchanged {{
            background-color: #f8f8f8;
        }}
        .resume-summary {{
            margin-bottom: 20px;
            padding: 10px;
            background-color: #f8f8f8;
            border-radius: 5px;
        }}
    </style>
    <div class="resume-diff-container">
        <h2>Resume Comparison</h2>
        <div class="resume-summary">
            <p><strong>Left Resume:</strong> {left_filename}</p>
            <p><strong>Right Resume:</strong> {right_filename}</p>
            <p><strong>Sections Compared:</strong> {len(section_comparisons)}</p>
        </div>
    """
    
    # Sort sections by similarity (lowest first to highlight differences)
    sorted_sections = sorted(section_comparisons.items(), 
                            key=lambda x: (x[1]['left_only'] or x[1]['right_only'], x[1]['similarity']))
    
    # Add each section
    for section_name, comparison in sorted_sections:
        # Format section header with similarity percentage
        similarity_pct = int(comparison['similarity'] * 100)
        
        if comparison['left_only']:
            section_class = "left-only"
            section_status = "Only in Left Resume"
        elif comparison['right_only']:
            section_class = "right-only"
            section_status = "Only in Right Resume"
        else:
            section_class = ""
            section_status = f"Similarity: {similarity_pct}%"
        
        html_output += f"""
        <div class="section-header {section_class}">
            {section_name.title()}
            <span class="section-similarity">{section_status}</span>
        </div>
        <div class="section-content">
        """
        
        # Add diff lines
        for line in comparison['diff']:
            if line.startswith('+ '):
                html_output += f'<p class="diff-line diff-added">{line}</p>'
            elif line.startswith('- '):
                html_output += f'<p class="diff-line diff-removed">{line}</p>'
            elif line.startswith('? '):
                # Skip the hint lines
                continue
            else:
                html_output += f'<p class="diff-line diff-unchanged">{line[2:]}</p>'
        
        html_output += "</div>"
    
    html_output += "</div>"
    return html_output

def extract_skills_from_resume(text):
    """
    Extract skills from resume text using common skill keywords
    """
    # Common technical skills
    tech_skills = [
        'python', 'java', 'javascript', 'c\+\+', 'c#', 'ruby', 'php', 'swift', 'kotlin',
        'html', 'css', 'sql', 'nosql', 'react', 'angular', 'vue', 'node', 'django', 'flask',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'jira', 'agile',
        'machine learning', 'ai', 'data science', 'big data', 'hadoop', 'spark', 'tableau',
        'power bi', 'excel', 'word', 'powerpoint', 'photoshop', 'illustrator', 'figma',
        'ui/ux', 'scrum', 'devops', 'ci/cd', 'rest api', 'graphql', 'microservices'
    ]
    
    # Common soft skills
    soft_skills = [
        'communication', 'leadership', 'teamwork', 'problem solving', 'critical thinking',
        'time management', 'organization', 'creativity', 'adaptability', 'flexibility',
        'project management', 'attention to detail', 'analytical', 'interpersonal',
        'negotiation', 'presentation', 'public speaking', 'writing', 'research', 'planning'
    ]
    
    # Combine all skills
    all_skills = tech_skills + soft_skills
    
    # Find skills in the text
    found_skills = []
    for skill in all_skills:
        if re.search(r'\b' + skill + r'\b', text.lower()):
            found_skills.append(skill)
    
    return found_skills

def compare_resume_skills(left_text, right_text):
    """
    Compare skills between two resumes
    """
    left_skills = set(extract_skills_from_resume(left_text))
    right_skills = set(extract_skills_from_resume(right_text))
    
    common_skills = left_skills.intersection(right_skills)
    left_only_skills = left_skills - right_skills
    right_only_skills = right_skills - left_skills
    
    return {
        'common': sorted(list(common_skills)),
        'left_only': sorted(list(left_only_skills)),
        'right_only': sorted(list(right_only_skills))
    }

def generate_skills_comparison_html(skills_comparison):
    """
    Generate HTML for skills comparison
    """
    html_output = """
    <style>
        .skills-container {
            font-family: Arial, sans-serif;
            margin-top: 20px;
        }
        .skills-section {
            margin-bottom: 15px;
        }
        .skills-header {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .skills-list {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
        }
        .skill-tag {
            background-color: #f0f0f0;
            padding: 5px 10px;
            border-radius: 15px;
            display: inline-block;
            font-size: 14px;
        }
        .common-skill {
            background-color: #e0f0e0;
        }
        .left-skill {
            background-color: #f0e0e0;
        }
        .right-skill {
            background-color: #e0e0f0;
        }
    </style>
    <div class="skills-container">
        <h3>Skills Comparison</h3>
    """
    
    # Common skills
    html_output += """
        <div class="skills-section">
            <div class="skills-header">Common Skills:</div>
            <div class="skills-list">
    """
    for skill in skills_comparison['common']:
        html_output += f'<span class="skill-tag common-skill">{skill}</span>'
    html_output += """
            </div>
        </div>
    """
    
    # Left only skills
    html_output += """
        <div class="skills-section">
            <div class="skills-header">Skills only in Left Resume:</div>
            <div class="skills-list">
    """
    for skill in skills_comparison['left_only']:
        html_output += f'<span class="skill-tag left-skill">{skill}</span>'
    html_output += """
            </div>
        </div>
    """
    
    # Right only skills
    html_output += """
        <div class="skills-section">
            <div class="skills-header">Skills only in Right Resume:</div>
            <div class="skills-list">
    """
    for skill in skills_comparison['right_only']:
        html_output += f'<span class="skill-tag right-skill">{skill}</span>'
    html_output += """
            </div>
        </div>
    </div>
    """
    
    return html_output
