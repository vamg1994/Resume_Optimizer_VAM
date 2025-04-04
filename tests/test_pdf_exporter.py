import pytest
from pathlib import Path
from src.exporters.pdf_exporter import ResumePDF, generate_resume_pdf
from src.models.resume import Resume

@pytest.fixture
def sample_resume_data():
    return {
        "name": "John Doe",
        "contact": ["john.doe@email.com", "LinkedIn: /in/johndoe", "(123) 456-7890"],
        "professional_summary": "Experienced data analyst with over 6 years of experience...",
        "work_experience": [
            {
                "title": "Senior Data Analyst",
                "company": "Tech Corp",
                "dates": "2020-Present",
                "responsibilities": [
                    "Led data analysis projects",
                    "Developed dashboards"
                ]
            }
        ],
        "education": [
            {
                "degree": "Master of Science in Data Analytics",
                "institution": "University Name",
                "dates": "2018-2020",
                "details": ["Specialized in machine learning", "GPA: 3.9/4.0"]
            }
        ],
        "skills": {
            "Technical": ["Python", "SQL", "Tableau"],
            "Soft Skills": ["Leadership", "Communication"]
        }
    }

def test_pdf_initialization():
    pdf = ResumePDF()
    assert pdf is not None
    assert pdf.title == "Resume"

def test_pdf_spanish_initialization():
    pdf = ResumePDF(language="Spanish")
    assert pdf is not None
    assert pdf.title == "CV"

def test_pdf_generation(sample_resume_data, tmp_path):
    output_path = tmp_path / "test_resume.pdf"
    success = generate_resume_pdf(sample_resume_data, output_path=str(output_path))
    assert success
    assert output_path.exists()
    assert output_path.stat().st_size > 0

def test_pdf_content(sample_resume_data, tmp_path):
    output_path = tmp_path / "test_resume.pdf"
    generate_resume_pdf(sample_resume_data, output_path=str(output_path))
    
    # Basic content validation
    with open(output_path, 'rb') as f:
        content = f.read()
        assert b"John Doe" in content
        assert b"Senior Data Analyst" in content
        assert b"Tech Corp" in content

def test_invalid_resume_data(tmp_path):
    invalid_data = {"name": "John Doe"}  # Missing required fields
    output_path = tmp_path / "test_resume.pdf"
    success = generate_resume_pdf(invalid_data, output_path=str(output_path))
    assert not success

def test_pdf_margins():
    pdf = ResumePDF()
    assert pdf.l_margin == 15
    assert pdf.t_margin == 15
    assert pdf.r_margin == 15

def test_pdf_font_sizes():
    pdf = ResumePDF()
    pdf.add_header("Test Name")
    assert pdf.font_size == 14  # Header font size
    
    pdf.add_section_header("Test Section")
    assert pdf.font_size == 10  # Section font size 