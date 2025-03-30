import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_responsiveness_tests(state):
    """Generates responsiveness test cases for different screen sizes."""
    website_content = state["website_content"]
    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["website_content"],
        template=(
            "Analyze website content: {website_content} and generate responsiveness test cases. "
            "Ensure proper rendering on mobile (375x667), tablet (768x1024), and desktop (1440x900) resolutions. "
            "Check for flex/grid issues, text wrapping, and touch gestures."
        ),
    )

    chain = LLMChain(llm=groq_llm, prompt=prompt)
    test_cases = chain.run({"website_content": website_content})

    return {"Responsiveness_Tests": test_cases}
