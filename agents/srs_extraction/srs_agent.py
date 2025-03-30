import io
import os
import fitz  # PyMuPDF for PDF text extraction
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.schema import AIMessage  # Import AIMessage to handle response
from dotenv import load_dotenv
import tiktoken  # For token counting

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TOKEN_LIMIT = 2000  # Keep a safe margin under 6000 limit

# Initialize Groq API
groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

# Tokenizer setup
def count_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-4")  # Use GPT-4 encoding (works for most LLMs)
    return len(encoding.encode(text))

# Extract text from PDF efficiently
def extract_text_from_pdf(pdf_bytes):
    """Extracts and cleans text from a PDF file using PyMuPDF (fitz)."""
    text = ""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")  # Open PDF from bytes

    for page in doc:
        extracted_text = page.get_text("text")  # Extract text from page
        if extracted_text:
            text += extracted_text.strip() + "\n"

    return text.strip() if text.strip() else "No text found in PDF."

# Split text into manageable chunks
def split_text(text, max_tokens=TOKEN_LIMIT):
    """Splits text into chunks that fit within the API token limit."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_tokens = 0

    for word in words:
        word_tokens = count_tokens(word)  # Count tokens in word
        if current_tokens + word_tokens > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_tokens = word_tokens
        else:
            current_chunk.append(word)
            current_tokens += word_tokens

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

# Summarize each chunk and combine results
def summarize_test_requirements(pdf_text):
    """Summarizes key test requirements from extracted PDF text using Groq API."""

    if not pdf_text.strip():
        return {"error": "No text extracted from PDF"}

    text_chunks = split_text(pdf_text)  # Split into API-compatible chunks
    summaries = []

    prompt = PromptTemplate(
        input_variables=["chunk_text"],
        template="Extract the key test case requirements from the following document section:\n\n{chunk_text}\n\nSummarize in bullet points."
    )

    for i, chunk in enumerate(text_chunks):
        print(f"\n🔹 Processing Chunk {i+1}/{len(text_chunks)} (Tokens: {count_tokens(chunk)})")
        summary = (prompt | groq_llm).invoke({"chunk_text": chunk})

        if isinstance(summary, AIMessage):
            summary = summary.content  # Extract text content

        summaries.append(summary.strip())

    # Combine summaries
    final_summary = "\n".join(summaries)

    return {"summary": final_summary}

if __name__ == "__main__":
    pdf_path = "SRS[1].pdf"  # Change this to your PDF file path

    # Read PDF file as bytes
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # Extract text from PDF
    extracted_text = extract_text_from_pdf(pdf_bytes)
    print("\n🔹 Extracted Text from PDF (First 500 chars):\n", extracted_text[:500])  # Print preview

    # Summarize test requirements using Groq API
    summary_result = summarize_test_requirements(extracted_text)

    if "error" in summary_result:
        print("\n❌ Error:", summary_result["error"])
    else:
        print("\n✅ Summarized Test Requirements:\n", summary_result["summary"])
