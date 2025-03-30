import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_integration_tests(state):
    """Generates test cases for frontend-backend interaction and API integrations."""
    figma_json = state["figma_json"]
    requirements_content = state["requirements_content"]
    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["figma_json", "requirements_content"],
        template=(
            "Analyze UI elements from Figma JSON: {figma_json} and user requirements: {requirements_content}. "
            "Generate integration test cases to verify seamless API calls, form submissions, "
            "user authentication, database interactions, error handling, and session management."
        ),
    )

    chain = LLMChain(llm=groq_llm, prompt=prompt)
    test_cases = chain.run({"figma_json": figma_json, "requirements_content": requirements_content})

    return {"Integration_Tests": test_cases}
