import os
import logging
from pathlib import Path
from typing import Optional, Union
import magic
from ..config.settings import MAX_FILE_SIZE, SUPPORTED_FILE_TYPES

logger = logging.getLogger(__name__)

def read_markdown_file(file_path: Union[str, Path]) -> str:
    """Read markdown file with error handling"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading markdown file {file_path}: {str(e)}")
        raise

def validate_file(file_path: Union[str, Path]) -> Optional[str]:
    """Validate file type and size"""
    try:
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds maximum limit of {MAX_FILE_SIZE/1024/1024}MB")

        # Check file type
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(str(file_path))
        
        if file_type not in SUPPORTED_FILE_TYPES:
            raise ValueError(f"Unsupported file type: {file_type}")
            
        return file_type
    except Exception as e:
        logger.error(f"Error validating file {file_path}: {str(e)}")
        raise

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and invalid characters"""
    # Remove path traversal attempts
    filename = os.path.basename(filename)
    
    # Replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    return filename

def create_temp_file(content: bytes, suffix: str) -> Path:
    """Create a temporary file with the given content"""
    import tempfile
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(content)
            return Path(tmp_file.name)
    except Exception as e:
        logger.error(f"Error creating temporary file: {str(e)}")
        raise

def cleanup_temp_file(file_path: Union[str, Path]) -> None:
    """Clean up temporary file"""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        logger.error(f"Error cleaning up temporary file {file_path}: {str(e)}")
        raise

def format_text_block(text: str, width: int = 120) -> str:
    """Format text block with proper wrapping"""
    import textwrap
    return textwrap.fill(text, width=width)

def validate_resume_structure(data: dict) -> bool:
    """Validate resume structure"""
    from ..models.resume import Resume
    try:
        Resume(**data)
        return True
    except Exception as e:
        logger.error(f"Invalid resume structure: {str(e)}")
        return False 