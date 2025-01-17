import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
import os
from assistant_manager import AssistantManager
from utils import read_markdown_file
import re
import html
from markitdown import MarkItDown
import tempfile

# Load environment variables
load_dotenv()

# Initialize AssistantManager
@st.cache_resource
def get_assistant():
    if not os.getenv("OPENAI_API_KEY"):
        st.error("OpenAI API key not found in environment variables")
        return None
    return AssistantManager()

# Page configuration
st.set_page_config(
    page_title="ATS Resume Generator",
    page_icon="📄",
    layout="wide",
    menu_items={
        'About':
        "VAM Resume Optimizer - Created by Virgilio Madrid",
        'Get Help': "https://readme.so/editor"
    })

# Configure Streamlit for development
st.set_option('client.showErrorDetails', True)

def main():
    
    st.title("VAM Resume Optimizer")

    # Initialize the assistant
    assistant = get_assistant()

    # Move all input elements to sidebar
    with st.sidebar:
        st.title("Input Information")

        # Initialize resume content with default resume
        try:
            default_resume_content = read_markdown_file(file_path="resume.md")
            st.success("Default resume template loaded!")
        except Exception as e:
            st.error(f"Error loading default resume: {str(e)}")
            return

        # Optional file upload to override default resume
        uploaded_file = st.file_uploader(
            "Upload your resume (optional)",
            type=['md', 'pdf', 'txt', 'docx'],
            help="Upload to override the default resume"
        )

        if uploaded_file is not None:
            try:
                file_type = uploaded_file.type
                
                if file_type == "application/pdf":
                    # Create a temporary file to save the PDF
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        pdf_path = tmp_file.name
                    
                    try:
                        # Initialize Markitdown
                        md = MarkItDown()
                        # Convert PDF to markdown
                        result = md.convert(pdf_path)
                        if result and result.text_content:
                            resume_content = result.text_content
                            st.success("PDF successfully converted to text!")
                        else:
                            st.error("Could not extract text from PDF.")
                            resume_content = default_resume_content
                    finally:
                        # Clean up temporary file
                        if os.path.exists(pdf_path):
                            os.unlink(pdf_path)
                
                elif file_type == "text/markdown" or file_type == "text/plain":
                    resume_content = uploaded_file.getvalue().decode()
                    st.success("File uploaded successfully!")
                
                elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    # Handle DOCX files if needed
                    st.error("DOCX support coming soon!")
                    resume_content = default_resume_content
                
                else:
                    st.error(f"Unsupported file type: {file_type}")
                    resume_content = default_resume_content
                    
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
                resume_content = default_resume_content
        else:
            resume_content = default_resume_content

        # Display current resume preview
        with st.expander("View Current Resume"):
            st.markdown(resume_content)

        # Form for job details
        with st.form("job_details_form"):
            # Language selection
            language = st.selectbox(
                "Language",
                options=["English", "Spanish"],
                index=0)

            # Job details
            job_name = st.text_input(
                "Job Name",
                placeholder="e.g., Data Analyst, ML Specialist")
            job_description = st.text_area("Job Description", height=200)
            location = st.text_input("Location",
                                   placeholder="e.g., Remote, New York",
                                   value="Remote")
            employer_info = st.text_area("Employer Information", height=100)

            submit_button = st.form_submit_button("Generate Resume Package")

    # Create tabs outside of the submit button condition
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Analysis", "Resume", "Cover Letter", "Download Files"])

    # Initialize session state for storing response if not exists
    if 'response' not in st.session_state:
        st.session_state.response = None

    if submit_button:
        if not job_name or not job_description or not employer_info:
            st.error("Please fill in all required fields")
            return

        with st.spinner("Generating your resume package..."):
            # Prepare input data
            input_data = {
                "language": language,
                "job_name": job_name,
                "job_description": job_description,
                "location": location,
                "employer_info": employer_info,
                "resume_content": resume_content
            }

            # Generate content using the assistant
            try:
                st.session_state.response = assistant.generate_resume_package(input_data)
                st.success("✨ Resume package generated successfully!")
                st.info("💡 Your resume has been optimized and formatted.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                return

    # Display content in tabs if response exists
    if st.session_state.response:
        response = st.session_state.response
        
        with tab1:
            st.markdown("### 📊 Resume Analysis")
            
            # Display full analysis if needed
            with st.expander("📝 Full Analysis", expanded=False):
                st.markdown("### Complete Analysis Report")
                st.markdown(response['analysis'])

        with tab2:
            st.title("📄 ATS-Optimized CV")
            
            # Personal Information Section
            with st.expander("👤 Personal Information", expanded=True):
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    response['structured_cv']['name'] = st.text_input(
                        "🏷️ Name", 
                        response['structured_cv']['name'],
                        help="Enter your full name"
                    )
                with col2:
                    contact_text = st.text_area(
                        "📞 Contact Information", 
                        "\n".join(response['structured_cv']['contact']),
                        help="Enter one contact detail per line"
                    )
                    response['structured_cv']['contact'] = [
                        line.strip() for line in contact_text.split('\n') 
                        if line.strip()
                    ]
            
            # Professional Summary Section
            with st.expander("📋 Professional Summary", expanded=True):
                st.markdown("---")
                response['structured_cv']['professional_summary'] = st.text_area(
                    "💼 Career Overview", 
                    response['structured_cv']['professional_summary'],
                    height=150,
                    help="Write a compelling summary of your professional background"
                )
            
            # Work Experience Section
            with st.expander("💼 Work Experience", expanded=True):
                st.markdown("---")
                col1, col2 = st.columns([5,1])
                with col1:
                    st.subheader("Work History")
                with col2:
                    if st.button("➕ Add Position", type="secondary"):
                        response['structured_cv']['work_experience'].append({
                            'title': 'New Position',
                            'company': 'Company Name',
                            'dates': 'Start Date - End Date',
                            'responsibilities': ['Add your responsibilities']
                        })
                        st.success("✅ New position added!")
                        st.rerun()

                for idx, job in enumerate(response['structured_cv']['work_experience']):
                    st.markdown(f"### Position {idx + 1}")
                    col1, col2, col3 = st.columns([4, 4, 1])
                    
                    with col1:
                        job['title'] = st.text_input(
                            "🏢 Job Title",
                            job['title'],
                            key=f"title_{idx}"
                        )
                        job['company'] = st.text_input(
                            "🏪 Company",
                            job['company'],
                            key=f"company_{idx}"
                        )
                    
                    with col2:
                        job['dates'] = st.text_input(
                            "📅 Employment Period",
                            job['dates'],
                            key=f"dates_{idx}"
                        )
                    
                    with col3:
                        st.markdown("#")  # Spacing
                        if st.button("🗑️", key=f"del_exp_{idx}", help="Delete this position"):
                            response['structured_cv']['work_experience'].pop(idx)
                            st.success("🗑️ Position removed!")
                            st.rerun()
                    
                    st.markdown("#### Key Responsibilities:")
                    for resp_idx, resp in enumerate(job['responsibilities']):
                        col1, col2 = st.columns([8, 1])
                        with col1:
                            new_resp = st.text_area(
                                f"📝 Responsibility {resp_idx + 1}",
                                resp,
                                height=100,
                                key=f"resp_{idx}_{resp_idx}"
                            )
                            job['responsibilities'][resp_idx] = new_resp
                        with col2:
                            st.markdown("#")  # Spacing
                            if st.button("➕", key=f"add_resp_{idx}_{resp_idx}"):
                                job['responsibilities'].insert(resp_idx + 1, "New responsibility")
                                st.rerun()
                            if st.button("🗑️", key=f"del_resp_{idx}_{resp_idx}"):
                                job['responsibilities'].pop(resp_idx)
                                st.rerun()
                    st.markdown("---")
            
            # Education Section
            with st.expander("🎓 Education", expanded=True):
                st.markdown("---")
                col1, col2 = st.columns([3,1])
                with col1:
                    st.subheader("Academic Background")
                with col2:
                    if st.button("➕ Add Education", type="secondary"):
                        response['structured_cv']['education'].append({
                            'degree': 'New Degree',
                            'institution': 'Institution Name',
                            'dates': 'Start Date - End Date',
                            'details': ['Add education details']
                        })
                        st.success("✅ New education entry added!")
                        st.rerun()

                for idx, edu in enumerate(response['structured_cv']['education']):
                    col1, col2, col3 = st.columns([0.85, 0.1, 0.05])
                    with col1:
                        st.subheader(f"Education {idx + 1}")
                        st.markdown(f"**{edu['degree']}**")
                        st.markdown(f"**{edu['institution']}**")
                        st.markdown(f"**{edu['dates']}**")
                    with col2:
                        if st.button("🗑️", key=f"del_edu_{idx}"):
                            response['structured_cv']['education'].pop(idx)
                            st.success("Education entry removed!")
                            st.rerun()
                    
                    # Make details editable
                    st.markdown("**Details:**")
                    updated_details = []
                    for detail_idx, detail in enumerate(edu['details']):
                        new_detail = st.text_area(
                            f"Detail {detail_idx + 1}",
                            detail,
                            height=100,
                            key=f"detail_{idx}_{detail_idx}"
                        )
                        updated_details.append(new_detail)
                    edu['details'] = updated_details
                    st.divider()
            
            # Skills Section
            with st.expander("🛠️ Skills", expanded=True):
                st.markdown("---")
                col1, col2 = st.columns([5,1])
                with col1:
                    st.subheader("Professional Skills")
                with col2:
                    new_category = st.text_input("🏷️ New Category Name")
                    if st.button("➕ Add Category", type="secondary") and new_category:
                        if new_category not in response['structured_cv']['skills']:
                            response['structured_cv']['skills'][new_category] = []
                            st.success(f"✅ Added new category: {new_category}")
                            st.rerun()

                for category in list(response['structured_cv']['skills'].keys()):
                    st.markdown(f"### {category}")
                    col1, col2 = st.columns([8,1])
                    with col1:
                        new_skill = st.text_input(
                            "➕ Add skill",
                            key=f"new_skill_{category}",
                            placeholder="Enter new skill and press Add"
                        )
                    with col2:
                        if st.button("🗑️", key=f"del_cat_{category}"):
                            del response['structured_cv']['skills'][category]
                            st.success(f"🗑️ Removed category: {category}")
                            st.rerun()
                    
                    if new_skill:
                        if st.button("Add", key=f"add_skill_{category}"):
                            if new_skill not in response['structured_cv']['skills'][category]:
                                response['structured_cv']['skills'][category].append(new_skill)
                                st.success(f"✅ Added {new_skill} to {category}")
                                st.rerun()

                    # Display existing skills
                    for skill_idx, skill in enumerate(response['structured_cv']['skills'][category]):
                        col1, col2 = st.columns([8,1])
                        with col1:
                            edited_skill = st.text_input(
                                f"Skill {skill_idx + 1}",
                                skill,
                                key=f"skill_{category}_{skill_idx}"
                            )
                            response['structured_cv']['skills'][category][skill_idx] = edited_skill
                        with col2:
                            if st.button("🗑️", key=f"del_skill_{category}_{skill_idx}"):
                                response['structured_cv']['skills'][category].pop(skill_idx)
                                st.success("🗑️ Skill removed!")
                                st.rerun()
                    st.markdown("---")

                # Update CV Button
                st.markdown("---")
                col1, col2 = st.columns([1,8])
                with col2:
                    if st.button("🔄 Update CV", type="secondary", use_container_width=True):
                        updated_cv = format_cv_from_structure(response['structured_cv'])
                        response['cv'] = updated_cv
                        st.session_state.response = response
                        st.success("✨ CV has been updated!")
                        st.markdown(updated_cv)

        with tab3:
            st.markdown("### Cover Letter")
            # Make cover letter editable with sections
            with st.expander("Edit Cover Letter", expanded=True):
                edited_cover_letter = st.text_area(
                    "Edit Cover Letter",
                    response['cover_letter'],
                    height=400,
                    key="cover_letter_editor"
                )
                if st.button("Update Cover Letter"):
                    response['cover_letter'] = edited_cover_letter
                    st.session_state.response = response
                    st.success("Cover Letter has been updated!")
            
            # Display the current version
            st.markdown("### Current Version")
            st.markdown(response['cover_letter'])

        with tab4:
            st.markdown("### Download Files")
            
            # Create combined text content with updated versions
            combined_text = f"""
ATS Resume Package

ANALYSIS
--------
{response['analysis']}

RESUME
------
{response['cv']}

COVER LETTER
-----------
{response['cover_letter']}
"""

            # Create markdown content with updated versions
            markdown_content = f"""
# ATS Resume Package

## Analysis
{response['analysis']}

## Resume
{response['cv']}

## Cover Letter
{response['cover_letter']}
"""
            
            # Create download section
            st.subheader("Download Options")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.download_button(
                    "📄 Download as Text",
                    combined_text,
                    file_name="ats_resume_package.txt",
                    mime="text/plain",
                    use_container_width=True)
            
            with col2:
                st.download_button(
                    "📝 Download as Markdown",
                    markdown_content,
                    file_name="ats_resume_package.md",
                    mime="text/markdown",
                    use_container_width=True)
            
            with col3:
                with st.expander("📑 PDF Settings"):
                    st.subheader("Font Sizes")
                    font_config = {
                        'header': {
                            'size': st.number_input('Header Font Size', 12, 36, 24),
                            'style': 'B'
                        },
                        'contact': {
                            'size': st.number_input('Contact Info Font Size', 8, 14, 10),
                            'style': ''
                        },
                        'section_header': {
                            'size': st.number_input('Section Headers Font Size', 10, 18, 14),
                            'style': 'B'
                        },
                        'summary': {
                            'size': st.number_input('Summary Font Size', 8, 14, 11),
                            'style': ''
                        }
                    }
                    
                    st.subheader("Spacing")
                    spacing_config = {
                        'header': st.number_input('Header Spacing', 5, 20, 10),
                        'contact': st.number_input('Contact Info Spacing', 3, 10, 5),
                        'section_header': st.number_input('Section Header Spacing', 5, 15, 10),
                        'section_gap': st.number_input('Section Gap', 3, 10, 5)
                    }

                if st.button("Generate PDF Resume", use_container_width=True):
                    try:
                        from export_pdf import generate_resume_pdf
                        success = generate_resume_pdf(
                            response['structured_cv'],
                            language=language,
                            output_path='resume.pdf',
                            font_config=font_config,
                            spacing_config=spacing_config
                        )
                        
                        if success:
                            with open('resume.pdf', 'rb') as pdf_file:
                                pdf_bytes = pdf_file.read()
                            
                            st.download_button(
                                label="📥 Download PDF",
                                data=pdf_bytes,
                                file_name="resume.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                            st.success("PDF Resume generated successfully!")
                        else:
                            st.error("Failed to generate PDF Resume")
                    except Exception as e:
                        st.error(f"Error generating PDF: {str(e)}")

            with col4:
                with st.expander("📘 DOCX Settings"):
                    st.subheader("Font Sizes")
                    docx_config = {
                        'name_size': st.number_input('Name Size', 12, 36, 24),
                        'contact_size': st.number_input('Contact Size', 8, 14, 10),
                        'heading_size': st.number_input('Heading Size', 10, 18, 14),
                        'title_size': st.number_input('Job Title Size', 10, 16, 12),
                        'body_size': st.number_input('Body Text Size', 8, 14, 11),
                        'margins': st.number_input('Margins (inches)', 0.3, 2.0, 0.5, step=0.1),
                        'line_spacing': st.number_input('Line Spacing', 0.3, 2.0, 1.15, step=0.05) #this means minimum is 0.3, maximum is 2.0, default is 1.15, and step is 0.05
                    }

                if st.button("Generate DOCX Resume", use_container_width=True):
                    try:
                        from export_docx import generate_resume_docx
                        success = generate_resume_docx(
                            structured_cv=response['structured_cv'],
                            language=language,
                            output_path='resume.docx',
                            config=docx_config
                        )
                        
                        if success:
                            with open('resume.docx', 'rb') as docx_file:
                                docx_bytes = docx_file.read()
                            
                            st.download_button(
                                label="📥 Download DOCX",
                                data=docx_bytes,
                                file_name="resume.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True
                            )
                            st.success("DOCX Resume generated successfully!")
                        else:
                            st.error("Failed to generate DOCX Resume")
                    except Exception as e:
                        st.error(f"Error generating DOCX: {str(e)}")

def format_cv_from_structure(structured_cv):
    """Helper function to format CV text from structured data"""
    cv_text = f"# {structured_cv['name']}\n\n"
    
    # Add contact information
    cv_text += "## Contact\n"
    for contact_item in structured_cv['contact']:
        cv_text += f"- {contact_item}\n"
    cv_text += "\n"
    
    # Add professional summary
    cv_text += "## Professional Summary\n"
    cv_text += structured_cv['professional_summary'] + "\n\n"
    
    # Add work experience
    cv_text += "## Work Experience\n\n"
    for job in structured_cv['work_experience']:
        cv_text += f"### {job['title']}\n"
        cv_text += f"**{job['company']}** | {job['dates']}\n"
        for resp in job['responsibilities']:
            cv_text += f"- {resp}\n"
        cv_text += "\n"
    
    # Add education
    cv_text += "## Education\n\n"
    for edu in structured_cv['education']:
        cv_text += f"### {edu['degree']}\n"
        cv_text += f"**{edu['institution']}** | {edu['dates']}\n"
        for detail in edu['details']:
            cv_text += f"- {detail}\n"
        cv_text += "\n"
    
    # Add skills
    cv_text += "## Skills\n\n"
    for category, skills in structured_cv['skills'].items():
        cv_text += f"### {category}\n"
        for skill in skills:
            cv_text += f"- {skill}\n"
        cv_text += "\n"
    
    return cv_text

def process_resume(resume_text):
    """Process the resume text and return structured data"""
    try:
        # Initialize session state for storing response if not exists
        if 'response' not in st.session_state:
            st.session_state.response = None

        # Get the assistant
        assistant = get_assistant()
        if not assistant:
            st.error("Could not initialize the assistant. Please check your API key.")
            return None

        # Process the resume using the assistant
        response = assistant.process_resume(
            resume_text=resume_text,
            job_name=st.session_state.get('job_name', ''),
            job_description=st.session_state.get('job_description', ''),
            employer_info=st.session_state.get('employer_info', ''),
            location=st.session_state.get('location', 'Remote')
        )

        return response

    except Exception as e:
        st.error(f"Error processing resume: {str(e)}")
        return None

if __name__ == "__main__":
    main()
