import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_unit_tests(state):
    """Generates frontend unit test cases for UI components and functions using Figma JSON and requirements."""
    figma_json = state["figma_json"]
    requirements_content = state["requirements_content"]
    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["figma_json", "requirements_content"],
        template=(
            "Analyze the frontend components from the Figma design: {figma_json} and user requirements: {requirements_content}. "
            "Generate unit test cases for UI components, form validation functions, event handlers, and JavaScript utilities. "
            "Ensure coverage of edge cases and different input scenarios."
        ),
    )

    chain = LLMChain(llm=groq_llm, prompt=prompt)
    test_cases = chain.run({"figma_json": figma_json, "requirements_content": requirements_content})

    return {"Unit_Tests": test_cases}
