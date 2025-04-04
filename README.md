# ATS Resume Optimizer

A powerful resume optimization tool that helps create ATS-friendly resumes and cover letters using AI.

## Features

- AI-powered resume optimization
- ATS-friendly formatting
- Multiple export formats (PDF, DOCX)
- Bilingual support (English/Spanish)
- File upload support (PDF, DOCX, Markdown)
- Real-time preview
- Detailed analysis and suggestions

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ats-resume.git
cd ats-resume
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root with:
```
OPENAI_API_KEY=your_api_key_here
ASSISTANT_ID=your_assistant_id_here
```

## Usage

1. Start the application:
```bash
streamlit run main.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Follow the on-screen instructions to:
   - Upload your resume
   - Enter job details
   - Generate optimized content
   - Download the results

## Project Structure

```
ats-resume/
├── src/
│   ├── core/           # Core functionality
│   ├── exporters/      # File export modules
│   ├── models/         # Data models
│   ├── utils/          # Utility functions
│   └── config/         # Configuration
├── tests/              # Test cases
├── templates/          # Template files
├── output/            # Generated files
└── logs/              # Application logs
```

## Development

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
pytest
```

3. Format code:
```bash
black .
```

4. Check code quality:
```bash
flake8
mypy .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Security

- All file uploads are validated for type and size
- Input sanitization is performed on all user inputs
- API keys are stored in environment variables
- Temporary files are properly cleaned up

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for the AI capabilities
- Streamlit for the web interface
- FPDF2 for PDF generation
- Python-docx for DOCX support 