import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_integration_tests(website_content):
    """Generates test cases for frontend-backend interaction and API integrations."""
    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["website_content"],
        template=(
            "Analyze frontend components from website content: {website_content} "
            "and generate integration test cases to verify seamless API calls, form submissions, "
            "user authentication, and database interactions."
        ),
    )

    chain = LLMChain(llm=groq_llm, prompt=prompt)
    test_cases = chain.run({"website_content": website_content})

    return {"Integration_Tests": test_cases}
