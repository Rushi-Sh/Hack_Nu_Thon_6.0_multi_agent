import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_responsiveness_tests(state):
    """
    Generates responsiveness test cases using Figma JSON and project requirements.
    Ensures UI adapts correctly to different screen sizes.
    """
    figma_json = state["figma_json"]
    requirements_content = state["requirements_content"]

    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["figma_json", "requirements_content"],
        template=(
            "Analyze UI design from Figma JSON: {figma_json} and project requirements: {requirements_content}. "
            "Generate structured test cases to validate UI responsiveness across the following resolutions:\n"
            "- Mobile (375x667, 414x896, 390x844)\n"
            "- Tablet (768x1024, 820x1180, 912x1368)\n"
            "- Desktop (1280x720, 1440x900, 1920x1080)\n"
            "\nTest cases should cover:\n"
            "- Proper layout adjustments and scaling\n"
            "- Grid/Flexbox responsiveness issues\n"
            "- Text wrapping, truncation, and scaling behavior\n"
            "- Touch gestures and interactive component scaling\n"
            "- Visibility of critical UI elements on different screens"
        ),
    )

    chain = LLMChain(llm=groq_llm, prompt=prompt)
    test_cases = chain.run({"figma_json": figma_json, "requirements_content": requirements_content})

    return {"Responsiveness_Tests": test_cases}
