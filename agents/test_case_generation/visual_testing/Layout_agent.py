import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_layout_tests(figma_json, requirements_content):
    state = {"figma_json": figma_json, "requirements_content": requirements_content}
    
    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["figma_json", "requirements_content"],
        template=(
            "Analyze the layout structure from Figma JSON: {figma_json} "
            "and the project requirements: {requirements_content}. "
            "Generate structured test cases for:\n"
            "- Layout consistency across screen sizes\n"
            "- Grid alignment and responsiveness\n"
            "- Spacing, margins, and padding compliance\n"
            "- Component positioning and relative alignment\n"
            "- Overlapping or misaligned UI elements"
        ),
    )

    chain = LLMChain(llm=groq_llm, prompt=prompt)
    test_cases = chain.run(state)  # Pass as a dictionary

    return {"Layout_Tests": test_cases}

