import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_unit_tests(website_content, figma_json):
    """Generates frontend unit test cases for UI components and functions."""
    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["website_content", "figma_json"],
        template=(
            "Analyze frontend components from website content: {website_content} and design from Figma JSON: {figma_json}. "
            "Generate unit test cases for individual UI components, form validation functions, and JavaScript utilities."
        ),
    )

    chain = LLMChain(llm=groq_llm, prompt=prompt)
    test_cases = chain.run({"website_content": website_content, "figma_json": figma_json})

    return {"Unit_Tests": test_cases}
