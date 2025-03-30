import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_api_tests(requirements_content):
    """Generates API test cases for response validation, status codes, authentication, and error handling."""
    
    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["requirements_content"],
        template=(
            """
            You are an expert in **API Testing** for web applications.
Analyze the API requirements from the provided document to generate structured API test cases.

### **INPUT DATA**
- **API Requirements**:  
  {requirements_content}

### **TASK**
1. **Generate comprehensive API test cases** covering:  
   - **Status Code Validation** (200, 400, 401, 403, 404, 500)
   - **Response Structure and Schema Validation**
   - **Authentication and Authorization Checks**
   - **Rate Limiting and Throttling**
   - **Error Handling and Edge Cases**
   - **API Payload Validation** for different request types (GET, POST, PUT, DELETE)
   - **HTTP Headers and Content Types**

2. **Each test case must include**:  
   - **test_id**: A unique identifier (e.g., "API-001")
   - **summary**: Short description of what is being tested
   - **priority**: Importance level (P1, P2, P3)
   - **tags**: Relevant categories as an array ["API", "Authentication", etc.]
   - **steps**: An array of test steps, each containing:
     - **step_number**: The sequence number
     - **action**: The action to perform
     - **expected_result**: What should happen if test passes

### **OUTPUT FORMAT (JSON)**
```json
{
  "API_Tests": [
    {
      "test_id": "API-001",
      "summary": "Verify successful user retrieval with valid authentication",
      "priority": "P1",
      "tags": ["API", "GET", "Authentication"],
      "steps": [
        {
          "step_number": 1,
          "action": "Prepare GET request to /api/users endpoint with valid authentication token",
          "expected_result": null
        },
        {
          "step_number": 2,
          "action": "Send the request",
          "expected_result": "Response status code is 200 OK"
        },
        {
          "step_number": 3,
          "action": "Validate response body",
          "expected_result": "Response contains valid JSON with expected user data schema"
        }
      ]
    }
  ]
}
            """
        ),
    )

    chain = LLMChain(llm=groq_llm, prompt=prompt)
    test_cases = chain.run({"requirements_content": requirements_content})

    return {"API_Tests": test_cases}
