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
    input_variables=["figma_data", "requirements_text"],
    template="""
    Generate a comprehensive and **detailed set of test cases** in **strict JSON format** based on the following inputs:

    **Figma Design Data:**
    {figma_data}

    **Requirements Document:**
    {requirements_text}

    **Test cases should cover:**
    - **Functional Testing** (cover all core functionalities)
    - **UI/UX Testing** (layout, responsiveness, and consistency)
    - **Accessibility Checks** (screen readers, keyboard navigation, color contrast)
    - **Performance Testing** (loading times, heavy data handling)
    - **Edge Cases & Error Handling** (unexpected inputs, extreme values)
    - **Security Testing** (login, authentication, data protection)
    - **Cross-Browser & Cross-Device Testing** (Chrome, Safari, Firefox, mobile, tablet)

    **JSON Format for Output:**
    ```json
    {
      "test_cases": [
        {
          "summary": "Short description of the test case",
          "priority": "P1/P2/P3",
          "tags": ["Relevant", "Tags"],
          "test_steps": [
            {
              "step": "Describe the test step",
              "expected_result": "Describe the expected outcome"
            }
          ]
        }
      ]
    }
    ```

    **Return 40 diverse test cases** following this format.  
    **Ensure the JSON is properly formatted without extra explanations or markdown.**
    """
)


    
    summaries = [(prompt | groq_llm).invoke({"chunk": chunk}).content.strip() for chunk in split_text(pdf_text)]
    return "\n".join(summaries)

# Main execution
if __name__ == "__main__":
    with open("SRS[1].pdf", "rb") as f:
        pdf_text = extract_text(f.read())
    
    print("\n✅ Summary:\n", summarize_text(pdf_text))