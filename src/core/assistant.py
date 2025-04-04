from openai import OpenAI
import os
import time
import json
import logging
from typing import Dict, Any
from ..models.resume import ResumePackage, JobDetails
from ..config.settings import OPENAI_API_KEY, ASSISTANT_ID, LOGGING_CONFIG

# Configure logging
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

class AssistantManager:
    def __init__(self):
        """Initialize the OpenAI assistant with proper error handling"""
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found in environment variables")
        
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        try:
            self.assistant = self.client.beta.assistants.retrieve(ASSISTANT_ID)
            logger.info("Successfully initialized OpenAI assistant")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI assistant: {str(e)}")
            raise

    def _create_thread(self) -> str:
        """Create a new thread for the conversation"""
        try:
            thread = self.client.beta.threads.create()
            return thread.id
        except Exception as e:
            logger.error(f"Failed to create thread: {str(e)}")
            raise

    def _wait_for_completion(self, thread_id: str, run_id: str, timeout: int = 300) -> None:
        """Wait for the assistant to complete processing with timeout"""
        start_time = time.time()
        
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError("Assistant response timeout after 5 minutes")

            try:
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id, run_id=run_id)
                
                if run_status.status == 'completed':
                    break
                elif run_status.status == 'failed':
                    raise Exception(f"Assistant run failed: {run_status.last_error}")
                
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error checking run status: {str(e)}")
                raise

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate the assistant's response"""
        try:
            # Clean up the response string
            response = response.strip()
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                response = response.split('```')[1].split('```')[0].strip()
            
            # Remove trailing commas
            response = response.replace(',}', '}').replace(',]', ']')
            
            # Parse JSON
            parsed_response = json.loads(response)
            
            # Validate using Pydantic model
            return ResumePackage(**parsed_response).dict()
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            raise ValueError(f"Failed to parse assistant response: {str(e)}")
        except Exception as e:
            logger.error(f"Error parsing response: {str(e)}")
            raise

    def generate_resume_package(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the resume package using the assistant with proper validation"""
        try:
            # Validate input data
            job_details = JobDetails(**input_data)
            
            # Create thread and send message
            thread_id = self._create_thread()
            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=json.dumps(input_data)
            )
            
            # Run the assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant.id
            )
            
            # Wait for completion
            self._wait_for_completion(thread_id, run.id)
            
            # Get the response
            messages = self.client.beta.threads.messages.list(thread_id=thread_id)
            if not messages.data:
                raise ValueError("No response received from assistant")
            
            response = messages.data[0].content[0].text.value
            if not response or not response.strip():
                raise ValueError("Empty response received from assistant")
            
            # Parse and validate the response
            return self._parse_response(response)
            
        except Exception as e:
            logger.error(f"Error generating resume package: {str(e)}")
            raise 