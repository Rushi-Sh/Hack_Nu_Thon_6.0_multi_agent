import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

# Load API Key from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

def suggest_test_updates(test_results):
    """
    Uses Gemini LLM to analyze test results and suggest improvements for test cases.
    
    :param test_results: A dictionary containing test results.
    :return: Suggested updates for test cases in structured JSON format.
    """
    
    prompt = f"""
    You are an AI that analyzes software test results and provides structured corrections.
    
    ### Input:
    The following test execution results:
    
    {json.dumps(test_results, indent=2)}
    
    ### Instructions:
    - Identify failed test cases and suggest specific fixes.
    - Improve edge case handling and boundary testing.
    - Ensure test cases follow best practices.
    
    ### Output Format:
    Provide the corrected test cases **strictly in JSON format** without any explanations, in the following structure:
    
    ```json
    {{
      "updated_test_cases": [
        {{
          "id": "TC001",
          "description": "Verify login with correct credentials",
          "status": "Failed",
          "error": "Incorrect password validation",
          "suggested_fix": "Update backend validation logic to allow case-insensitive passwords."
        }},
        {{
          "id": "TC002",
          "description": "Check UI button color change on hover",
          "status": "Passed"
        }}
      ]
    }}
    ```
    
    Return only valid JSON output. Do not add any additional text.
    """

    try:
        # Initialize Gemini model
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(prompt)
        
        raw_response = response.text.strip()
        print("Raw Response:", raw_response)  # Debugging output

        # Remove ```json and ``` if present
        if raw_response.startswith("```json"):
            raw_response = raw_response[7:]  # Remove ```json
        if raw_response.endswith("```"):
            raw_response = raw_response[:-3]  # Remove ```

        # Ensure cleaned response is valid JSON
        return json.loads(raw_response.strip())

    except json.JSONDecodeError:
        return {"error": "Gemini returned malformed JSON. Try refining the prompt."}

    except Exception as e:
        return {"error": f"Failed to generate updates: {str(e)}"}

# Example Usage
if __name__ == "__main__":
    sample_test_results = {
        "test_cases": [
            {
                "id": "TC001",
                "description": "Verify login with correct credentials",
                "status": "Failed",
                "error": "Incorrect password validation",
                "suggested_fix": None
            },
            {
                "id": "TC002",
                "description": "Check UI button color change on hover",
                "status": "Passed"
            }
        ]
    }

    updated_test_cases = suggest_test_updates(sample_test_results)
    print(json.dumps(updated_test_cases, indent=2))
