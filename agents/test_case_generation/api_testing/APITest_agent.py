import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_api_tests(requirements_content):
    """Generates API test cases for response validation, status codes, authentication, and error handling."""
    
    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["requirements_content"],
        template=(
            "Analyze the API requirements from the provided document: {requirements_content}. "
            "Generate API test cases focusing on:\n"
            "- Status code validation (200, 400, 401, 403, 404, 500, etc.)\n"
            "- Response structure and schema validation\n"
            "- Authentication and authorization checks\n"
            "- Rate limiting and throttling\n"
            "- Error handling and edge cases\n"
            "- API payload validation for different request types (GET, POST, PUT, DELETE)"
        ),
    )

    chain = LLMChain(llm=groq_llm, prompt=prompt)
    test_cases = chain.run({"requirements_content": requirements_content})

    return {"API_Tests": test_cases}
