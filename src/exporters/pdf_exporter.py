from fpdf import FPDF
import textwrap
from typing import Dict, List, Optional
from ..config.settings import PDF_SETTINGS
import logging

logger = logging.getLogger(__name__)

class ResumePDF(FPDF):
    def __init__(self, language: str = "English"):
        """Initialize PDF with language-specific settings"""
        super().__init__()
        self._configure_defaults()
        self._set_language(language)
        logger.info(f"Initialized PDF with language: {language}")

    def _configure_defaults(self):
        """Configure default PDF settings"""
        self.set_auto_page_break(auto=True, margin=PDF_SETTINGS["margins"]["top"])
        self.add_page()
        self.set_margins(
            left=PDF_SETTINGS["margins"]["left"],
            top=PDF_SETTINGS["margins"]["top"],
            right=PDF_SETTINGS["margins"]["right"]
        )

    def _set_language(self, language: str):
        """Set language-specific headers"""
        if language == "English":
            self.title = "Resume"
            self.headers = ["Professional Summary", "Work Experience", "Education", "Skills"]
        else:
            self.title = "CV"
            self.headers = ["Resumen Profesional", "Experiencia Laboral", "Educación", "Habilidades"]

    def add_header(self, name: str, spacing: float = PDF_SETTINGS["spacing"]):
        """Add name as header with error handling"""
        try:
            self.set_font('Times', 'B', PDF_SETTINGS["font_size"]["header"])
            self.cell(0, spacing, name, ln=True, align='C')
            self.ln(5)
        except Exception as e:
            logger.error(f"Error adding header: {str(e)}")
            raise

    def add_contact_info(self, contact_info: List[str]):
        """Add contact information section with wrapping"""
        try:
            self.set_font('Times', '', PDF_SETTINGS["font_size"]["body"])
            contact_line = ' | '.join(contact_info)
            wrapped_contact = textwrap.fill(contact_line, width=120)
            for line in wrapped_contact.split('\n'):
                self.cell(0, 5, line, ln=True, align='C')
            self.ln(5)
        except Exception as e:
            logger.error(f"Error adding contact info: {str(e)}")
            raise

    def add_section_header(self, title: str, spacing: float = PDF_SETTINGS["spacing"]):
        """Add section header with line"""
        try:
            self.set_font('Times', 'B', PDF_SETTINGS["font_size"]["section"])
            self.cell(0, spacing, title, ln=True)
            self.line(15, self.get_y(), 195, self.get_y())
            self.ln(5)
        except Exception as e:
            logger.error(f"Error adding section header: {str(e)}")
            raise

    def add_professional_summary(self, summary: str, spacing: float = PDF_SETTINGS["spacing"]):
        """Add professional summary section"""
        try:
            self.set_font('Times', '', PDF_SETTINGS["font_size"]["body"])
            wrapped_text = textwrap.fill(summary, width=120)
            for line in wrapped_text.split('\n'):
                self.cell(0, spacing, line, ln=True)
            self.ln(5)
        except Exception as e:
            logger.error(f"Error adding professional summary: {str(e)}")
            raise

    def add_work_experience(self, experience: List[Dict], spacing: float = PDF_SETTINGS["spacing"]):
        """Add work experience section"""
        try:
            for job in experience:
                self.set_font('Times', 'B', PDF_SETTINGS["font_size"]["section"])
                self.cell(0, spacing, f"{job['title']}", ln=True)
                
                self.set_font('Times', '', PDF_SETTINGS["font_size"]["body"])
                self.cell(0, spacing, f"{job['company']} | {job['dates']}", ln=True)
                
                for resp in job['responsibilities']:
                    self.cell(5, spacing, '-', ln=0)
                    wrapped_text = textwrap.fill(resp, width=120)
                    first_line = True
                    for line in wrapped_text.split('\n'):
                        if first_line:
                            self.cell(0, spacing, line, ln=True)
                            first_line = False
                        else:
                            self.cell(5, spacing, '', ln=0)
                            self.cell(0, spacing, line, ln=True)
                self.ln(3)
        except Exception as e:
            logger.error(f"Error adding work experience: {str(e)}")
            raise

    def add_education(self, education: List[Dict], spacing: float = PDF_SETTINGS["spacing"]):
        """Add education section"""
        try:
            for edu in education:
                self.set_font('Times', 'B', PDF_SETTINGS["font_size"]["section"])
                self.cell(0, spacing, f"{edu['degree']}", ln=True)
                
                self.set_font('Times', '', PDF_SETTINGS["font_size"]["body"])
                self.cell(0, spacing, f"{edu['institution']} | {edu['dates']}", ln=True)
                
                details_text = ', '.join(edu['details'])
                wrapped_details = textwrap.fill(details_text, width=120)
                for line in wrapped_details.split('\n'):        
                    self.cell(5, spacing, '-', ln=0)
                    self.cell(0, spacing, line, ln=True)
                self.ln(3)
        except Exception as e:
            logger.error(f"Error adding education: {str(e)}")
            raise

    def add_skills(self, skills: Dict[str, List[str]], spacing: float = PDF_SETTINGS["spacing"]):
        """Add skills section"""
        try:
            for category, skill_list in skills.items():
                self.set_font('Times', 'B', PDF_SETTINGS["font_size"]["section"])
                self.cell(0, spacing, category, ln=True)
                
                self.set_font('Times', '', PDF_SETTINGS["font_size"]["body"])
                skills_text = ', '.join(skill_list)
                wrapped_skills = textwrap.fill(skills_text, width=120)
                for line in wrapped_skills.split('\n'):
                    self.cell(0, spacing, line, ln=True)
                self.ln(3)
        except Exception as e:
            logger.error(f"Error adding skills: {str(e)}")
            raise

def generate_resume_pdf(structured_cv: Dict, language: str = "English", output_path: str = 'resume.pdf') -> bool:
    """Generate PDF resume from structured CV data"""
    try:
        pdf = ResumePDF(language=language)
        
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
        
        pdf.output(output_path)
        logger.info(f"Successfully generated PDF at {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        return False 