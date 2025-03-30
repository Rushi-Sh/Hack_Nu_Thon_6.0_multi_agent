import sys
import os
import fitz  # PyMuPDF for PDF text extraction

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.figma_extraction.figma_agent import fetch_figma_json
from agents.srs_extraction.srs_agent import summarize_test_requirements
from agents.website_extraction.website_agent import extract_all_content

def fetch_figma_json(figma_url):
    """Fetch Figma JSON data."""
    try:
        # Import the function locally to avoid circular import
        from agents.figma_extraction.figma_agent import fetch_figma_json as _fetch_figma_json
        return _fetch_figma_json(figma_url)
    except Exception as e:
        return {"error": f"Failed to fetch Figma JSON: {str(e)}"}

def fetch_pdf_text(pdf_bytes):
    """Extracts text from a PDF and summarizes test requirements."""
    try:
        pdf_text = ""
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        for page in doc:
            pdf_text += page.get_text("text") + "\n"

        if not pdf_text.strip():
            return {"error": "No readable text found in PDF."}

        summary = summarize_test_requirements(pdf_text)
        return {"summary": summary}

    except Exception as e:
        return {"error": f"Failed to process PDF: {str(e)}"}

def fetch_website_data(website_url):
    """Extracts HTML, CSS, and JS from a website."""
    try:
        content = extract_all_content(website_url)
        return content

    except Exception as e:
        return {"error": f"Failed to extract website data: {str(e)}"}
