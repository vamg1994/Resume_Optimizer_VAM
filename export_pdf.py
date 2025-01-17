from fpdf import FPDF
import textwrap

class ResumePDF(FPDF):
    def __init__(self, language="English", font_config=None, spacing_config=None):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.set_margins(left=15, top=15, right=15)
        
        # Set headers based on language
        if language == "English":
            self.title = "Resume"
            self.headers = ["Professional Summary", "Work Experience", "Education", "Skills"]
        else:
            self.title = "CV"
            self.headers = ["Resumen Profesional", "Experiencia Laboral", "Educación", "Habilidades"]

    def add_header(self, name,spacing=3.5):
        """Add name as header"""
        self.set_font('Times', 'B', 14)
        self.cell(0, spacing, name, ln=True, align='C')
        self.ln(5)

    def add_contact_info(self, contact_info):
        """Add contact information section"""
        self.set_font('Times', '', 10)
        # Join all contact info with ' | ' separator
        contact_line = ' | '.join(contact_info)
        # Wrap the contact line if it's too long
        wrapped_contact = textwrap.fill(contact_line, width=120)
        for line in wrapped_contact.split('\n'):
            self.cell(0, 5, line, ln=True, align='C')
        self.ln(5)

    def add_section_header(self, title,spacing=3.5):
        """Add section header with line"""
        self.set_font('Times', 'B', 10)
        self.cell(0, spacing, title, ln=True)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(5)

    def add_professional_summary(self, summary,spacing=3.5):
        """Add professional summary section"""
        self.set_font('Times', '', 10)
        wrapped_text = textwrap.fill(summary, width=95)
        for line in wrapped_text.split('\n'):
            self.cell(0, spacing, line, ln=True)
        self.ln(5)

    def add_work_experience(self, experience,spacing=3.5):
        """Add work experience section"""
        for job in experience:
            # Job title and company
            self.set_font('Times', 'B', 10)
            self.cell(0, spacing, f"{job['title']}", ln=True)
            
            # Company and dates
            self.set_font('Times', '', 10)
            self.cell(0, spacing, f"{job['company']} | {job['dates']}", ln=True)
            
            # Responsibilities
            self.set_font('Times', '', 10)
            for resp in job['responsibilities']:
                # Add dash instead of bullet point and indent
                self.cell(5, spacing, '-', ln=0)
                wrapped_text = textwrap.fill(resp, width=85)
                first_line = True
                for line in wrapped_text.split('\n'):
                    if first_line:
                        self.cell(0, spacing, line, ln=True)
                        first_line = False
                    else:
                        self.cell(5, spacing, '', ln=0)  # Indent
                        self.cell(0, spacing, line, ln=True)
            self.ln(3)

    def add_education(self, education,spacing=3.5):
        """Add education section"""
        for edu in education:
            self.set_font('Times', 'B', 10)
            self.cell(0, spacing, f"{edu['degree']}", ln=True)
            
            self.set_font('Times', '', 10)
            self.cell(0, spacing, f"{edu['institution']} | {edu['dates']}", ln=True)
            
            self.set_font('Times', '', 10)
            #create a wrapped list of details
            details_text = ', '.join(edu['details'])
            wrapped_details = textwrap.fill(details_text, width=95)
            for line in wrapped_details.split('\n'):        
                self.cell(5, spacing, '-', ln=0)  # Changed bullet to dash
                self.cell(0, spacing, line, ln=True)
            self.ln(3)

    def add_skills(self, skills,spacing=3.5):
        """Add skills section"""
        for category, skill_list in skills.items():
            self.set_font('Times', 'B', 10)
            self.cell(0, spacing, category, ln=True)
            
            self.set_font('Times', '', 8)
            # Create a wrapped list of skills
            skills_text = ', '.join(skill_list)
            wrapped_skills = textwrap.fill(skills_text, width=95)
            for line in wrapped_skills.split('\n'):
                self.cell(0, spacing, line, ln=True)
            self.ln(3)

def generate_resume_pdf(structured_cv, language="English", output_path='resume.pdf', font_config=None, spacing_config=None):
    """Generate PDF resume from structured CV data with custom configurations"""
    try:
        # Initialize PDF with configurations and language
        pdf = ResumePDF(language=language)
        
        # Add content sections with language-specific headers
        pdf.add_header(structured_cv['name'])
        pdf.add_contact_info(structured_cv['contact'])
        
        pdf.add_section_header(pdf.headers[0])
        pdf.add_professional_summary(structured_cv['professional_summary'])
        
        pdf.add_section_header(pdf.headers[1])
        pdf.add_work_experience(structured_cv['work_experience'])
        
        pdf.add_section_header(pdf.headers[2])
        pdf.add_education(structured_cv['education'])
        
        pdf.add_section_header(pdf.headers[3])
        pdf.add_skills(structured_cv['skills'])
        
        # Save the PDF
        pdf.output(output_path)
        return True
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return False

# Example usage with your dummy data
if __name__ == "__main__":
    # Test with dummy structured CV data
    structured_cv = {
        "name": "John Doe",
        "contact": [
            "john.doe@email.com",
            "LinkedIn: /in/johndoe",
            "(123) 456-7890",
            "City, Country"
        ],
        "professional_summary": "Experienced data analyst with over 6 years...",
        "work_experience": [
            {
                "title": "Senior Data Analyst",
                "company": "Tech Corp",
                "dates": "2020-Present",
                "responsibilities": [
                    "Led data analysis projects...",
                    "Developed dashboards..."
                ]
            }
        ],
        "education": [
            {
                "degree": "Master of Science in Data Analytics",
                "institution": "University Name",
                "dates": "2018-2020",
                "details": [
                    "Specialized in machine learning",
                    "GPA: 3.9/4.0"
                ]
            }
        ],
        "skills": {
            "Technical": ["Python", "SQL", "Tableau", "Power BI"],
            "Soft Skills": ["Leadership", "Communication", "Problem Solving"]
        }
    }
    
    success = generate_resume_pdf(structured_cv, 'example_resume.pdf')
    if success:
        print("PDF generated successfully!")   
