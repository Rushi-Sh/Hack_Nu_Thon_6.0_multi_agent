import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_performance_tests(website_content):
    """Generates test cases to measure frontend performance (load time, rendering speed)."""
    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["website_content"],
        template=(
            "Analyze website content: {website_content} and generate performance test cases. "
            "Check page load times, rendering delays, lazy loading efficiency, and script execution speed."
        ),
    )

    chain = LLMChain(llm=groq_llm, prompt=prompt)
    test_cases = chain.run({"website_content": website_content})

    return {"Performance_Tests": test_cases}
