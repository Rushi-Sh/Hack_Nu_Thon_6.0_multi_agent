import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_accessibility_tests(state):
    """Generates accessibility test cases following WCAG guidelines using Figma and website content."""
    figma_json = state["figma_json"]
    website_content = state["website_content"]
    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["figma_json", "website_content"],
        template=(
            "Analyze the UI elements from Figma JSON: {figma_json} and "
            "website content: {website_content}. Generate WCAG-compliant "
            "accessibility test cases, covering contrast, text size, keyboard navigation, "
            "ARIA labels, and screen reader compatibility."
        ),
    )

    chain = LLMChain(llm=groq_llm, prompt=prompt)
    test_cases = chain.run({"figma_json": figma_json, "website_content": website_content})

    return {"Accessibility_Tests": test_cases}
