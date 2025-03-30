import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_integration_tests(state):
    """Generates test cases for frontend-backend interaction and API integrations."""
    figma_json = state["figma_json"]
    requirements_content = state["requirements_content"]
    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["figma_json", "requirements_content"],
        template=(
           """
           You are an expert in **Integration Testing** for web applications.
Analyze UI elements from **Figma JSON** and **user requirements** to generate structured integration test cases.

### **INPUT DATA**
- **Figma UI Elements**:  
  {figma_json}
- **Software Requirements**:  
  {requirements_content}

### **TASK**
1. **Generate comprehensive integration test cases** covering:  
   - **API Calls** (data fetching, posting, updating)
   - **Form Submissions** (data persistence to backend)
   - **User Authentication** (login, registration, password reset)
   - **Database Interactions** (CRUD operations)
   - **Error Handling** (API errors, network failures)
   - **Session Management** (token handling, timeouts, refresh)
   - **Cross-Component Communication** (data sharing between components)

2. **Each test case must include**:  
   - **test_id**: A unique identifier (e.g., "INT-001")
   - **summary**: Short description of what is being tested
   - **priority**: Importance level (P1, P2, P3)
   - **tags**: Relevant categories as an array ["Integration", "API", etc.]
   - **steps**: An array of test steps, each containing:
     - **step_number**: The sequence number
     - **action**: The action to perform
     - **expected_result**: What should happen if test passes

### **OUTPUT FORMAT (JSON)**
```json
{
  "Integration_Tests": [
    {
      "test_id": "INT-001",
      "summary": "Verify user login with valid credentials",
      "priority": "P1",
      "tags": ["Integration", "Authentication", "API"],
      "steps": [
        {
          "step_number": 1,
          "action": "Navigate to login page",
          "expected_result": null
        },
        {
          "step_number": 2,
          "action": "Enter valid username and password",
          "expected_result": null
        },
        {
          "step_number": 3,
          "action": "Click login button",
          "expected_result": "API call is made with correct credentials format"
        },
        {
          "step_number": 4,
          "action": "Monitor API response",
          "expected_result": "Authentication token is received and stored"
        },
        {
          "step_number": 5,
          "action": null,
          "expected_result": "User is redirected to dashboard with authenticated user data displayed"
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

    return {"Integration_Tests": test_cases}
