from openai import OpenAI
import os
import time
import re
import json
import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AssistantManager:
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds

    def __init__(self):
        """Initialize the AssistantManager with retry logic"""
        self.client = None
        self.assistant = None
        self._initialize_with_retry()

    def _initialize_with_retry(self):
        """Initialize the OpenAI client and retrieve the assistant with retry logic"""
        for attempt in range(self.MAX_RETRIES):
            try:
                # Initialize OpenAI client
                self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                
                # Retrieve the assistant
                agent_id = os.getenv("agent_id")
                if not agent_id:
                    raise ValueError("agent_id not found in environment variables")
                
                self.assistant = self.client.beta.assistants.retrieve(agent_id)
                logger.info(f"Successfully initialized AssistantManager with assistant: {self.assistant.id}")
                return
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.MAX_RETRIES - 1:
                    logger.info(f"Retrying in {self.RETRY_DELAY} seconds...")
                    time.sleep(self.RETRY_DELAY)
                else:
                    raise Exception(f"Failed to initialize AssistantManager after {self.MAX_RETRIES} attempts: {str(e)}")

    def generate_resume_package(self, input_data):
        """Generate the resume package using the assistant"""
        try:
            # Create a thread
            thread = self.client.beta.threads.create()

            # Add the message to the thread
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=json.dumps(input_data))

            # Run the assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id, assistant_id=self.assistant.id)

            # Wait for completion with timeout
            timeout = 300  # 5 minutes timeout
            start_time = time.time()

            while True:
                if time.time() - start_time > timeout:
                    raise TimeoutError(
                        "Assistant response timeout after 5 minutes")

                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id, run_id=run.id)

                if run_status.status == 'completed':
                    break
                elif run_status.status == 'failed':
                    raise Exception(
                        f"Assistant run failed: {run_status.last_error}")

                time.sleep(1)

            # Get the response
            messages = self.client.beta.threads.messages.list(
                thread_id=thread.id)

            if not messages.data:
                raise ValueError("No response received from assistant")

            # Parse the response
            response = messages.data[0].content[0].text.value

            if not response or not response.strip():
                raise ValueError("Empty response received from assistant")

            # Log the raw response for debugging
            logger.info("Raw assistant response received")
            logger.debug(f"Response content: {response[:500]}...")

            # Clean up the response string
            # Remove any potential markdown code block markers and clean the JSON string
            response = response.strip()
            # Handle different markdown code block formats
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                response = response.split('```')[1].split('```')[0].strip()
            
            # Remove any trailing commas before closing braces/brackets
            response = re.sub(r',(\s*[}\]])', r'\1', response)
            
            try:
                # Parse the JSON response with detailed error handling
                try:
                    parsed_response = json.loads(response)
                except json.JSONDecodeError as e:
                    # Try to identify the specific parsing error
                    error_line = str(e).split(' line ')[1].split()[0]
                    error_col = str(e).split(' column ')[1].split()[0]
                    content_lines = response.split('\n')
                    error_context = content_lines[int(error_line)-1] if int(error_line) <= len(content_lines) else "Context not available"
                    
                    logger.error(f"JSON parsing error at line {error_line}, column {error_col}")
                    logger.error(f"Error context: {error_context}")
                    logger.debug(f"Full response content:\n{response}")
                    
                    raise ValueError(
                        f"Failed to parse assistant response as JSON. Error at line {error_line}, column {error_col}. "
                        f"Context: {error_context}")
            except Exception as e:
                logger.error(f"Unexpected error during JSON parsing: {str(e)}")
                logger.debug(f"Invalid JSON content: {response}")
                raise ValueError(f"Failed to parse assistant response: {str(e)}")

            # Validate required keys
            required_keys = ['cv', 'structured_cv', 'cover_letter', 'analysis']
            missing_keys = [
                key for key in required_keys if key not in parsed_response
            ]
            if missing_keys:
                raise ValueError(
                    f"Missing required keys in response: {', '.join(missing_keys)}"
                )

            # Validate structured_cv format with detailed checks
            structured_cv = parsed_response.get('structured_cv', {})
            if not isinstance(structured_cv, dict):
                raise ValueError("structured_cv must be a dictionary")

            required_cv_sections = [
                'name', 'contact','professional_summary', 'work_experience', 'education', 'skills'
            ]
            missing_sections = [
                section for section in required_cv_sections
                if section not in structured_cv
            ]
            if missing_sections:
                raise ValueError(
                    f"Missing required sections in structured_cv: {', '.join(missing_sections)}"
                )

            # Validate data types and nested structures
            if not isinstance(structured_cv.get('name', ''), str):
                raise ValueError("Name must be a string")
                
            contact_info = structured_cv.get('contact', [])
            if not isinstance(contact_info, list):
                raise ValueError("Contact information must be a list")
            if not all(isinstance(item, str) for item in contact_info):
                raise ValueError("All contact information items must be strings")

            professional_summary = structured_cv.get('professional_summary', '')
            if not isinstance(professional_summary, str):
                raise ValueError("Professional summary must be a string")

            work_experience = structured_cv.get('work_experience', [])
            if not isinstance(work_experience, list):
                raise ValueError("Work experience must be a list")
            for idx, job in enumerate(work_experience):
                if not isinstance(job, dict):
                    raise ValueError(f"Work experience item {idx} must be a dictionary")
                required_job_fields = ['title', 'company', 'dates', 'responsibilities']
                missing_fields = [field for field in required_job_fields if field not in job]
                if missing_fields:
                    raise ValueError(f"Work experience item {idx} missing required fields: {', '.join(missing_fields)}")
                if not isinstance(job.get('responsibilities', []), list):
                    raise ValueError(f"Work experience item {idx} responsibilities must be a list")

            education = structured_cv.get('education', [])
            if not isinstance(education, list):
                raise ValueError("Education must be a list")
            for idx, edu in enumerate(education):
                if not isinstance(edu, dict):
                    raise ValueError(f"Education item {idx} must be a dictionary")
                required_edu_fields = ['degree', 'institution', 'dates', 'details']
                missing_fields = [field for field in required_edu_fields if field not in edu]
                if missing_fields:
                    raise ValueError(f"Education item {idx} missing required fields: {', '.join(missing_fields)}")
                if not isinstance(edu.get('details', []), list):
                    raise ValueError(f"Education item {idx} details must be a list")

            skills = structured_cv.get('skills', {})
            if not isinstance(skills, dict):
                raise ValueError("Skills must be a dictionary")
            for category, skill_list in skills.items():
                if not isinstance(skill_list, list):
                    raise ValueError(f"Skills category '{category}' must contain a list of skills")
                if not all(isinstance(skill, str) for skill in skill_list):
                    raise ValueError(f"All skills in category '{category}' must be strings")

            logger.info("Successfully validated resume package structure")
            return parsed_response

        except TimeoutError as e:
            logger.error(f"Timeout error: {str(e)}")
            raise
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
