import os
import json
import re
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq API
groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

def generate_manual_test_cases(ui_desc, requirements_text):
    """Generates structured test cases based on UI description and requirements text."""

    if not ui_desc and not requirements_text:
        return {"error": "At least one valid input source (UI data or requirements) must be provided"}
    
    prompt = PromptTemplate(
        input_variables=["ui_desc", "requirements_text"],
        template="""
        Generate structured test cases based on the following inputs:

        **UI description Data:**  
        {ui_desc}

        **Requirements Document:**  
        {requirements_text}

        **Focus Areas:**  
        - Functional testing  
        - Layout and UI validation  
        - Accessibility checks  
        - Edge cases  
        - Error handling  

        **Return the response in valid JSON format only, structured as follows:**  

        {{
            "summary": "Brief description of the test scenario",
            "priority": "P1 or P2 or P3",
            "tags": ["Tag1", "Tag2"],
            "test_cases": [
                {{
                    "step": "Action to be performed",
                    "expected_result": "Expected outcome"
                }},
                {{
                    "step": "Next action",
                    "expected_result": "Next expected outcome"
                }}
            ]
        }}

        Ensure the response is strictly valid JSON with no extra text or explanations.
        """
    )

    input_data = {
        "ui_desc": ui_desc if ui_desc else "No UI description provided",
        "requirements_text": requirements_text if requirements_text else "No requirements provided"
    }
    
    try:
        response = (prompt | groq_llm).invoke(input_data)

        if response and hasattr(response, "content") and response.content:
            content = response.content.strip()

            # Attempt to extract JSON using regex (handles cases where LLM outputs extra text)
            json_match = re.search(r'```json\s*([\s\S]*?)```', content)
            json_str = json_match.group(1).strip() if json_match else content

            try:
                # Parse JSON
                json_response = json.loads(json_str)
                return {
                    "message": "Test cases generated successfully",
                    "test_cases": json_response
                }
            except json.JSONDecodeError as json_err:
                return {"error": f"Failed to parse LLM response as JSON: {str(json_err)}", "raw_response": content}
        else:
            return {"error": "No valid response from AI"}
    except Exception as e:
        return {"error": f"Test generation failed: {str(e)}"}
