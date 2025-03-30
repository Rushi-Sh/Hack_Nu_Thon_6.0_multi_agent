import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_security_tests(requirements_content):
    """Generates backend security test cases for vulnerability detection."""
    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["requirements_content"],
        template=(
            "Analyze backend security measures from the extracted document: {requirements_content}. "
            "Generate test cases to detect SQL injection, authentication bypass, session hijacking, and data exposure vulnerabilities."
        ),
    )

    chain = LLMChain(llm=groq_llm, prompt=prompt)
    test_cases = chain.run({"requirements_content": requirements_content})

    return {"Security_Tests": test_cases}
