import io
import os
import fitz  # PyMuPDF for PDF text extraction
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def extract_text_from_pdf(pdf_bytes):
    """Extracts text from a PDF file using PyMuPDF (fitz)."""
    text = ""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")  # Open PDF from bytes

    for page in doc:
        extracted_text = page.get_text("text")  # Extract text from page
        if extracted_text:
            text += extracted_text + "\n"

    return text.strip() if text.strip() else "No text found in PDF."

def summarize_test_requirements(pdf_text):
    """Summarizes key test requirements from extracted PDF text using Groq API."""

    if not pdf_text.strip():
        return {"error": "No text extracted from PDF"}

    # Initialize Groq API
    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["pdf_text"],
        template="Extract the key test case requirements from the following document:\n\n{pdf_text}\n\nSummarize in bullet points."
    )

    # Use LangChain's updated method
    summary = (prompt | groq_llm | (lambda x: x['text'])).invoke({"pdf_text": pdf_text})

    return {"summary": summary}


if __name__ == "__main__":
    pdf_path = "sample_test_cases.pdf"  # Change this to your PDF file path

    # Read PDF file as bytes
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # Extract text from PDF
    extracted_text = extract_text_from_pdf(pdf_bytes)
    print("\n🔹 Extracted Text from PDF:\n", extracted_text[:500])  # Print first 500 chars

    # Summarize test requirements using Groq API
    summary_result = summarize_test_requirements(extracted_text)
    
    if "error" in summary_result:
        print("\n❌ Error:", summary_result["error"])
    else:
        print("\n✅ Summarized Test Requirements:\n", summary_result["summary"])
