import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_accessibility_tests(state):
    """
    Generates accessibility test cases following WCAG guidelines
    using Figma JSON and Requirements Content.
    """
    figma_json = state["figma_json"]
    requirements_content = state["requirements_content"]  # Fixed variable name

    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["figma_json", "requirements_content"],
        template=(
            "Analyze the UI elements from Figma JSON: {figma_json} and "
            "the project requirements: {requirements_content}. "
            "Generate WCAG-compliant accessibility test cases, covering: \n"
            "- Contrast ratios \n"
            "- Text size and readability \n"
            "- Keyboard navigation support \n"
            "- ARIA labels and semantic HTML compliance \n"
            "- Screen reader compatibility and focus order."
        ),
    )

    chain = LLMChain(llm=groq_llm, prompt=prompt)
    test_cases = chain.run({"figma_json": figma_json, "requirements_content": requirements_content})

    return {"Accessibility_Tests": test_cases}
