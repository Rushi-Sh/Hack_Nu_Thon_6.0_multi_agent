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

def extract_json_from_response(response_text):
    """
    Extracts and returns the pure JSON content from the LLM response.
    """
    try:
        # Try parsing directly as JSON (if LLM returns plain JSON)
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass  # If direct parsing fails, proceed to regex extraction

    # Attempt to extract JSON from within text using regex
    json_match = re.search(r'\{[\s\S]*\}', response_text)
    if json_match:
        json_str = json_match.group(0)  # Extract matched JSON content
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            return {"error": f"Extracted JSON is invalid: {str(e)}", "raw_response": response_text}

    # If no valid JSON found, return error
    return {"error": "Failed to extract valid JSON from response", "raw_response": response_text}


def generate_manual_test_cases(ui_desc, requirements_text):
    """Generates structured test cases based on UI description and requirements text."""

    if not ui_desc and not requirements_text:
        return {"error": "At least one valid input source (UI data or requirements) must be provided"}
    
    prompt = PromptTemplate(
        input_variables=["ui_desc", "requirements_text"],
        template="""
        Generate structured test cases based on the following inputs:

        *UI description Data:*  
        {ui_desc}
        
        *Requirements Document:*  
        {requirements_text}
        
        *Focus Areas:*  
        - Functional testing  
        - Layout and UI validation  
        - Accessibility checks  
        - Edge cases  
        - Error handling  

        *Return the response in the following valid JSON format, with no extra text or markdown formatting:*  

        {{
            "message": "Test cases generated successfully",
            "test_cases": {{
                "priority": "P1",
                "summary": "Figma Design Data Validation",
                "tags": [
                    "Functional testing",
                    "Layout and UI validation",
                    "Accessibility checks"
                ],
                "test_cases": [
                    {{
                        "expected_result": "The data should contain both Layout_agent and Usability_agent",
                        "step": "Check if Figma design data exists"
                    }},
                    {{
                        "expected_result": "The data should contain 3 FRAME objects with correct IDs, names, and sizes",
                        "step": "Verify Layout_agent data"
                    }},
                    {{
                        "expected_result": "The data should contain 6 INSTANCE objects with correct IDs, names, and sizes",
                        "step": "Verify Usability_agent data"
                    }},
                    {{
                        "expected_result": "No duplicate IDs should exist in both Layout_agent and Usability_agent",
                        "step": "Check for duplicate IDs"
                    }},
                    {{
                        "expected_result": "All data types should be correct (FRAME or INSTANCE)",
                        "step": "Check for invalid data types"
                    }},
                    {{
                        "expected_result": "All objects should be accessible and have ARIA attributes",
                        "step": "Check for accessibility"
                    }},
                    {{
                        "expected_result": "Test data with varying sizes and positions",
                        "step": "Test edge cases"
                    }},
                    {{
                        "expected_result": "Test data with invalid or missing data to ensure proper error handling",
                        "step": "Test error handling"
                    }}
                ]
            }}
        }}
        """
    )

    input_data = {
        "ui_desc": ui_desc if ui_desc else "No UI description provided",
        "requirements_text": requirements_text if requirements_text else "No requirements provided"
    }
    
    try:
        response = (prompt | groq_llm).invoke(input_data)

        if response and hasattr(response, "content") and response.content:
            extracted_json = extract_json_from_response(response.content)
            return extracted_json
        else:
            return {"error": "No valid response from AI"}
    
    except Exception as e:
        return {"error": f"Test generation failed: {str(e)}"}