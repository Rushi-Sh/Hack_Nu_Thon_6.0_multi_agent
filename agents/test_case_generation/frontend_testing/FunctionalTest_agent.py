import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_functional_tests(website_content, figma_json):
    """Generates functional UI test cases for buttons, forms, and interactive elements."""
    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["website_content", "figma_json"],
        template=(
            "Analyze website functionalities from content: {website_content} and UI design from Figma JSON: {figma_json}. "
            "Generate test cases to verify buttons, forms, modals, and dropdowns work correctly."
        ),
    )

    chain = LLMChain(llm=groq_llm, prompt=prompt)
    test_cases = chain.run({"website_content": website_content, "figma_json": figma_json})

    return {"Functional_Tests": test_cases}
