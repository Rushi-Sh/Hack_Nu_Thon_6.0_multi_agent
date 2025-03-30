import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_usability_tests(state):
    """Generates usability test cases based on website UI and user requirements."""
    website_content = state["website_content"]
    pdf_summary = state.get("requirements_content", "")
    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["website_content", "pdf_summary"],
        template=(
            "Analyze website usability based on UI content: {website_content} and user requirements summary: {pdf_summary}. "
            "Generate test cases ensuring intuitive navigation, proper feedback messages, error prevention, and clear call-to-actions (CTAs)."
        ),
    )

    chain = LLMChain(llm=groq_llm, prompt=prompt)
    test_cases = chain.run({"website_content": website_content, "pdf_summary": pdf_summary})

    return {"Usability_Tests": test_cases}
