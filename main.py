import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
import os
from assistant_manager import AssistantManager
from utils import read_markdown_file
import re
import html

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
            "Upload your resume.md file (optional)",
            type=['md'],
            help="Upload to override the default resume")

        if uploaded_file:
            resume_content = uploaded_file.read().decode()
            st.success("Custom resume uploaded successfully!")
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
            st.markdown("### Resume Analysis")
            # Make analysis editable
            edited_analysis = st.text_area(
                "Edit Analysis",
                response['analysis'],
                height=400,
                key="analysis_editor"
            )
            if st.button("Update Analysis"):
                response['analysis'] = edited_analysis
                st.session_state.response = response
                st.success("Analysis has been updated!")

        with tab2:
            st.markdown("### ATS-Optimized CV")
            
            # Create expandable cards for each section
            with st.expander("Personal Information", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    # Update name in structured data
                    response['structured_cv']['name'] = st.text_input(
                        "Name", 
                        response['structured_cv']['name']
                    )
                with col2:
                    # Update contact info in structured data
                    contact_text = st.text_area(
                        "Contact Information", 
                        "\n".join(response['structured_cv']['contact'])
                    )
                    response['structured_cv']['contact'] = [
                        line.strip() for line in contact_text.split('\n') 
                        if line.strip()
                    ]
            
            with st.expander("Professional Summary", expanded=True):
                # Update professional summary in structured data
                response['structured_cv']['professional_summary'] = st.text_area(
                    "Summary", 
                    response['structured_cv']['professional_summary'],
                    height=150
                )
            
            with st.expander("Work Experience", expanded=True):
                for idx, job in enumerate(response['structured_cv']['work_experience']):
                    st.subheader(f"Position {idx + 1}")
                    col1, col2 = st.columns(2)
                    with col1:
                        job['title'] = st.text_input(f"Title {idx}", job['title'])
                        job['company'] = st.text_input(f"Company {idx}", job['company'])
                    with col2:
                        job['dates'] = st.text_input(f"Dates {idx}", job['dates'])
                    
                    # Make responsibilities editable
                    st.markdown("**Responsibilities:**")
                    updated_resp = []
                    for resp_idx, resp in enumerate(job['responsibilities']):
                        new_resp = st.text_area(
                            f"Responsibility {resp_idx + 1}",
                            resp,
                            height=100,
                            key=f"resp_{idx}_{resp_idx}"
                        )
                        updated_resp.append(new_resp)
                    job['responsibilities'] = updated_resp
                    st.divider()
            
            with st.expander("Education", expanded=True):
                for idx, edu in enumerate(response['structured_cv']['education']):
                    st.subheader(f"Education {idx + 1}")
                    col1, col2 = st.columns(2)
                    with col1:
                        edu['degree'] = st.text_input(f"Degree {idx}", edu['degree'])
                        edu['institution'] = st.text_input(f"Institution {idx}", 
                                                        edu['institution'])
                    with col2:
                        edu['dates'] = st.text_input(f"Dates {idx}", edu['dates'])
                    
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
            
            with st.expander("Skills", expanded=True):
                for category, skills in response['structured_cv']['skills'].items():
                    st.subheader(category)
                    updated_skills = st.text_area(
                        f"Skills - {category}",
                        "\n".join(skills),
                        height=100,
                        key=f"skills_{category}"
                    ).split("\n")
                    response['structured_cv']['skills'][category] = [
                        skill.strip() for skill in updated_skills if skill.strip()
                    ]
            
            # Add a button to regenerate the CV text based on edited content
            if st.button("Update CV"):
                # Update the CV text based on edited structured content
                updated_cv = format_cv_from_structure(response['structured_cv'])
                response['cv'] = updated_cv
                st.session_state.response = response
                st.success("CV has been updated!")
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
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.download_button(
                    "📄 Download as Text File",
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
            
            # PDF download button
            with col3:
                if st.button("📑 Generate PDF Resume"):
                    try:
                        from exportingcvpdf import generate_resume_pdf
                        
                        # Generate PDF
                        success = generate_resume_pdf(
                            response['structured_cv'],
                            'resume.pdf'
                        )
                        
                        if success:
                            # Read the generated PDF
                            with open('resume.pdf', 'rb') as pdf_file:
                                pdf_bytes = pdf_file.read()
                            
                            # Create download button
                            st.download_button(
                                label="📥 Download PDF Resume",
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

if __name__ == "__main__":
    main()
