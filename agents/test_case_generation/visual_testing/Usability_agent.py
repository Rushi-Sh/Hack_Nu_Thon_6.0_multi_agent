import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_usability_tests(state):
    """
    Generates usability test cases based on UI design from Figma JSON
    and user requirements from the provided document.
    """
    figma_json = state["figma_json"]
    requirements_content = state["requirements_content"]

    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["figma_json", "requirements_content"],
        template=(
            "Analyze UI usability based on design elements from Figma JSON: {figma_json} "
            "and user requirements from the document: {requirements_content}. "
            "Generate structured usability test cases ensuring:\n"
            "- Intuitive navigation with clear menus and interactive elements\n"
            "- Proper user feedback for errors, actions, and confirmations\n"
            "- Clear and accessible Call-to-Action (CTA) buttons\n"
            "- Error prevention mechanisms (e.g., input validation, undo actions)\n"
            "- Minimal cognitive load, ensuring users can accomplish tasks efficiently\n"
            "- Compliance with usability heuristics like visibility, consistency, and control"
        ),
    )

    chain = LLMChain(llm=groq_llm, prompt=prompt)
    test_cases = chain.run({"figma_json": figma_json, "requirements_content": requirements_content})

    return {"Usability_Tests": test_cases}
