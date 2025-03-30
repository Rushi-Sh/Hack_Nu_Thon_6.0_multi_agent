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
            """
        You are an expert in **Accessibility Testing**, following **WCAG** guidelines. 
        Analyze the UI elements from **Figma JSON** and the **project requirements** to generate structured accessibility test cases.

        ### **INPUT DATA**
        - **Figma UI Elements**:  
        {figma_json}
        - **Software Requirements**:  
        {requirements_content}

        ### **TASK**
        Generate WCAG-compliant accessibility test cases covering:  
        - Contrast Ratios (e.g., sufficient text/background contrast)  
        - Text Size & Readability (e.g., minimum font size, legibility)  
        - Keyboard Navigation Support (e.g., tab order, focus state)  
        - ARIA Labels & Semantic HTML Compliance  
        - Screen Reader Compatibility & Focus Order  

        ### **OUTPUT FORMAT (JSON)**
        ```json
        {
        "Accessibility_Tests": [
            {
            "test_id": "ACC-001",
            "summary": "Verify text contrast ratio meets WCAG AA guidelines",
            "priority": "P1",
            "tags": ["Accessibility", "Contrast", "WCAG"],
            "steps": [
                {
                "step_number": 1,
                "action": "Identify all text elements and their background colors",
                "expected_result": null
                },
                {
                "step_number": 2,
                "action": "Check contrast ratio using WCAG contrast evaluation tool",
                "expected_result": "All text maintains minimum 4.5:1 contrast ratio for normal text and 3:1 for large text"
                }
            ]
            }
        ]
        }
            """
        ),
    )

    chain = LLMChain(llm=groq_llm, prompt=prompt)
    test_cases = chain.run({"figma_json": figma_json, "requirements_content": requirements_content})

    return {"Accessibility_Tests": test_cases}
