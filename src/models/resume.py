from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from datetime import datetime

class WorkExperience(BaseModel):
    title: str = Field(..., min_length=2, max_length=100)
    company: str = Field(..., min_length=2, max_length=100)
    dates: str = Field(..., min_length=4, max_length=20)
    responsibilities: List[str] = Field(..., min_items=1)

    @validator('dates')
    def validate_dates(cls, v):
        # Basic date format validation
        if not any(char.isdigit() for char in v):
            raise ValueError("Dates must contain at least one number")
        return v

class Education(BaseModel):
    degree: str = Field(..., min_length=2, max_length=100)
    institution: str = Field(..., min_length=2, max_length=100)
    dates: str = Field(..., min_length=4, max_length=20)
    details: List[str] = Field(..., min_items=1)

class Skills(BaseModel):
    technical: List[str] = Field(..., min_items=1)
    soft: List[str] = Field(..., min_items=1)

class Resume(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    contact: List[str] = Field(..., min_items=1, max_items=5)
    professional_summary: str = Field(..., min_length=50, max_length=2000)
    work_experience: List[WorkExperience] = Field(..., min_items=1)
    education: List[Education] = Field(..., min_items=1)
    skills: Skills

    @validator('contact')
    def validate_contact(cls, v):
        for item in v:
            if not any(char.isalnum() for char in item):
                raise ValueError("Contact information must contain alphanumeric characters")
        return v

class ResumePackage(BaseModel):
    cv: str
    structured_cv: Resume
    cover_letter: str
    analysis: str

class JobDetails(BaseModel):
    language: str = Field(..., regex="^(English|Spanish)$")
    job_name: str = Field(..., min_length=2, max_length=100)
    job_description: str = Field(..., min_length=50)
    location: str = Field(..., min_length=2, max_length=100)
    employer_info: str = Field(..., min_length=50)
    resume_content: str = Field(..., min_length=50) 