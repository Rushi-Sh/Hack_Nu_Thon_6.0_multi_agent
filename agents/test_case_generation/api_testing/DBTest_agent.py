import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_database_tests(requirements_content):
    """Generates database test cases for schema validation and query optimization."""
    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["requirements_content"],
        template=(
            "Analyze database schema and queries from the extracted requirements document: {requirements_content}. "
            "Generate test cases for schema validation, data consistency, indexing efficiency, and query performance."
        ),
    )

    chain = LLMChain(llm=groq_llm, prompt=prompt)
    test_cases = chain.run({"requirements_content": requirements_content})

    return {"Database_Tests": test_cases}
