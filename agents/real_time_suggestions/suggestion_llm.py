import os
import google.generativeai as genai
from database import fetch_test_case_by_id  
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_suggestions_for_test_case(test_case_id):
    """Fetch a test case by ID and generate optimized improvement suggestions using Gemini."""
    test_case = fetch_test_case_by_id(test_case_id)

    if not test_case:
        print(f"⚠️ No test case found for ID: {test_case_id}")
        return

    prompt = f"""
    You are a highly skilled **Software Testing Expert** with expertise in writing, analyzing, and optimizing test cases.
    Your task is to critically analyze the given test case and provide **detailed suggestions** for improvements.

    **Instructions:**
    1. **Review & Improve:** Identify any gaps, ambiguities, or inefficiencies in the test case.
    2. **Enhance Coverage:** Suggest missing test scenarios, including edge cases and boundary conditions.
    3. **Optimization Tips:** Recommend best practices to refine the test case for better readability and execution.
    4. **Bug Prediction:** Identify potential issues that might not be covered and propose solutions.
    5. **Automation Potential:** Assess whether this test case is suitable for automation and, if so, suggest an approach.

    **Test Case for Review:**
    ```
    {test_case}
    ```

    **Expected Output:**
    - **Detailed feedback on improvements**
    - **New test scenarios and edge cases**
    - **Optimized version of the test case (if applicable)**
    - **Suggestions for automation**
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-pro")  
        response = model.generate_content(prompt)

        print("✅ Suggestions for Test Case Improvement:")
        print(response.text)

    except Exception as e:
        print(f"⚠️ Error generating suggestions: {e}")

if __name__ == "__main__":
    generate_suggestions_for_test_case("67e9a3489a5ef20b0ef0a856")
