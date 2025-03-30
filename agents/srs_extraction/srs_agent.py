import os
import fitz  # PyMuPDF
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import tiktoken  # Token counting

# Load API key
load_dotenv()
groq_llm = ChatGroq(model="llama3-8b-8192", api_key=os.getenv("GROQ_API_KEY"))

# Count tokens
def count_tokens(text):
    return len(tiktoken.encoding_for_model("gpt-4").encode(text))

# Extract text from PDF
def extract_text(pdf_bytes):
    return "\n".join(page.get_text("text").strip() for page in fitz.open(stream=pdf_bytes, filetype="pdf"))

# Split text into chunks
def split_text(text, max_tokens=2000):
    words, chunks, chunk = text.split(), [], []
    tokens = 0
    for word in words:
        word_tokens = count_tokens(word)
        if tokens + word_tokens > max_tokens:
            chunks.append(" ".join(chunk))
            chunk, tokens = [word], word_tokens
        else:
            chunk.append(word)
            tokens += word_tokens
    if chunk:
        chunks.append(" ".join(chunk))
    return chunks

# Summarize document
def summarize_text(pdf_text):
    if not pdf_text.strip():
        return "No text found."
    
    prompt = PromptTemplate(
        input_variables=["chunk"],
        template="Summarize key test requirements from this section:\n\n{chunk}\n\nBullet points."
    )
    
    summaries = [(prompt | groq_llm).invoke({"chunk": chunk}).content.strip() for chunk in split_text(pdf_text)]
    return "\n".join(summaries)

# Main execution
if __name__ == "__main__":
    with open("SRS[1].pdf", "rb") as f:
        pdf_text = extract_text(f.read())
    
    print("\n✅ Summary:\n", summarize_text(pdf_text))