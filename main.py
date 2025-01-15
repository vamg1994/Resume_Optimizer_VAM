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

    # Main content area with tabs
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
                response = assistant.generate_resume_package(input_data)

                # Create tabs for different sections
                tab1, tab2, tab3, tab4 = st.tabs(
                    ["Analysis", "Resume", "Cover Letter", "Download Files"])

                with tab1:
                    st.markdown("### Resume Analysis")
                    st.markdown(response['analysis'])

                with tab2:
                    st.markdown("### ATS-Optimized CV")
                    st.markdown(response['cv'])

                    # Create combined text content with enhanced formatting
                    combined_text = f"""
───────────────────────────────────────────────────────────────────────────────
                         ATS-OPTIMIZED RESUME PACKAGE                          
───────────────────────────────────────────────────────────────────────────────

===================================
              ANALYSIS             
===================================

{response['analysis']}

-----------------------------------

===================================
              RESUME              
===================================

{response['cv']}

-----------------------------------

===================================
           COVER LETTER           
===================================

{response['cover_letter']}

───────────────────────────────────────────────────────────────────────────────
                            End of Package                                     
───────────────────────────────────────────────────────────────────────────────
"""
                    
                    # Create markdown formatted content
                    markdown_content = f"""# ATS-OPTIMIZED RESUME PACKAGE

## Analysis

{response['analysis']}

## Resume

{response['cv']}

## Cover Letter

{response['cover_letter']}

---
*Generated by ATS Resume Generator*
"""

                with tab3:
                    st.markdown("### Cover Letter")
                    st.markdown(response['cover_letter'])

                st.success("✨ Resume package generated successfully!")
                st.info(
                    "💡 Your resume has been optimized and formatted."
                )
                
                with tab4:
                    st.markdown("### Download Files")
                    
                    # Create download section
                    st.subheader("Download Options")
                    col1, col2 = st.columns(2)
                    
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

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
