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

def generate_test_cases(figma_data, requirements_text):
    """
    Generates test cases based on Figma JSON and requirements content.
    """
    if not figma_data and not requirements_text:
        return {"error": "At least one valid input source (figma data or requirements) must be provided"}
    
    prompt = PromptTemplate(
    input_variables=["figma_data", "requirements_text"],
    template="""
    Generate structured test cases based on the following inputs:
    
    *Figma Design Data:*  
    {figma_data}
    
    *Requirements Document:*  
    {requirements_text}
    
    *Focus Areas:*  
    - Functional testing  
    - Layout and UI validation  
    - Accessibility checks  
    - Edge cases  
    - Error handling  

    *Return the response in valid JSON format only, structured as follows:*  

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
        "figma_data": str(figma_data) if figma_data else "No Figma data provided",
        "requirements_text": requirements_text if requirements_text else "No requirements provided"
    }
    
    try:
        response = (prompt | groq_llm).invoke(input_data)
        
        if response and hasattr(response, "content") and response.content:
            # Extract JSON from the response
            content = response.content
            
            # Try to find JSON in the content
            json_match = re.search(r'(?:json)?\s*([\s\S]*?)', content)
            if json_match:
                # Extract JSON from code block
                json_str = json_match.group(1).strip()
            else:
                # If no code blocks found, try to find JSON directly
                json_str = content.strip()
            
            try:
                # Parse the content as JSON and return a Python dictionary
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

if __name__ == "__main__":  # Fixed this line
    example_figma_json = {
        "Layout_agent": "Login page has a centered form with aligned fields.",
        "Usability_agent": "Navigation buttons should be large and accessible."
    }
    example_requirements = "Users must be able to log in with email and password. Errors should be displayed clearly."
    
    test_cases = generate_test_cases(example_figma_json, example_requirements)
    print("\n✅ Generated Test Cases:")
    print(json.dumps(test_cases, indent=2))  # Pretty print the JSON