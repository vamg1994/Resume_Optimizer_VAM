import os
import logging
import json

def read_markdown_file(file_path=None, file_content=None):
    """
    Read and process markdown file content
    Args:
        file_path: Path to the markdown file (for default resume)
        file_content: Content from uploaded file (optional override)
    """
    try:
        if file_content is not None:
            return file_content.strip()
        elif file_path:
            with open(file_path, 'r') as file:
                return file.read().strip()
        else:
            raise Exception("No file content provided")
    except Exception as e:
        raise Exception(f"Error reading markdown file: {str(e)}")