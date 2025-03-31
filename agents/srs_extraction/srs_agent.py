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

# Extract structured requirements
def extract_requirements(pdf_text):
    if not pdf_text.strip():
        return "No text found."
    
    prompt = PromptTemplate(
        input_variables=["requirements_text"],
        template="""
        Extract and categorize all key requirements from the following Software Requirements Document (SRS):

        **Requirements Document:**
        {requirements_text}

        **Categories to extract:**
        - **Functional Requirements** (core system behavior and features)
        - **Non-Functional Requirements** (performance, security, usability, reliability, scalability)
        - **Domain-Specific Requirements** (industry-specific rules, standards, compliance)
        - **Business Logic** (decision-making rules, calculations, workflows)
        - **User Interface (UI/UX) Requirements** (layout, navigation, accessibility)
        - **Integration Requirements** (third-party APIs, databases, external services)
        - **Security & Compliance Requirements** (authentication, encryption, GDPR, HIPAA, etc.)
        - **Performance & Load Requirements** (response times, scalability, data handling)
        - **Error Handling & Edge Cases** (validation, incorrect input handling)
        - **Cross-Platform & Cross-Browser Requirements** (desktop, mobile, web, different OS)

        **Return the extracted requirements in strict JSON format:**
        ```json
        {{
          "functional_requirements": [
            "Requirement 1",
            "Requirement 2"
          ],
          "non_functional_requirements": [
            "Requirement 1",
            "Requirement 2"
          ],
          "domain_specific_requirements": [
            "Requirement 1",
            "Requirement 2"
          ],
          "business_logic": [
            "Requirement 1",
            "Requirement 2"
          ],
          "ui_ux_requirements": [
            "Requirement 1",
            "Requirement 2"
          ],
          "integration_requirements": [
            "Requirement 1",
            "Requirement 2"
          ],
          "security_requirements": [
            "Requirement 1",
            "Requirement 2"
          ],
          "performance_requirements": [
            "Requirement 1",
            "Requirement 2"
          ],
          "error_handling_requirements": [
            "Requirement 1",
            "Requirement 2"
          ],
          "cross_platform_requirements": [
            "Requirement 1",
            "Requirement 2"
          ]
        }}
        ```
        **Ensure the JSON is properly formatted with no additional text, explanations, or markdown.**
        """
    )

    structured_requirements = [
        (prompt | groq_llm).invoke({"requirements_text": chunk}).content.strip()
        for chunk in split_text(pdf_text)
    ]
    
    return "\n".join(structured_requirements)

# Main execution
if __name__ == "__main__":
    with open("SRS.pdf", "rb") as f:
        pdf_text = extract_text(f.read())
    
    print("\n✅ Extracted Requirements:\n", extract_requirements(pdf_text))
