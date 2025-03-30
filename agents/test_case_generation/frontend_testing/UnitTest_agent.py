import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_unit_tests(state):
    """Generates frontend unit test cases for UI components and functions using Figma JSON and requirements."""
    figma_json = state["figma_json"]
    requirements_content = state["requirements_content"]
    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["figma_json", "requirements_content"],
        template=(
           """
           You are an expert in **Unit Testing** for frontend applications.
Analyze frontend components from **Figma design** and **user requirements** to generate structured unit test cases.

### **INPUT DATA**
- **Figma UI Elements**:  
  {figma_json}
- **Software Requirements**:  
  {requirements_content}

### **TASK**
1. **Generate comprehensive unit test cases** covering:  
   - **UI Components** (rendering, props, state management)
   - **Form Validation Functions** (input validation rules)
   - **Event Handlers** (click, change, submit handlers)
   - **JavaScript Utilities** (helper functions, formatters)
   - **State Management Logic** (reducers, actions, selectors)
   - **Edge Cases** (boundary values, error states)
   - **Conditional Rendering** (showing/hiding elements based on state)

2. **Each test case must include**:  
   - **test_id**: A unique identifier (e.g., "UNIT-001")
   - **summary**: Short description of what is being tested
   - **priority**: Importance level (P1, P2, P3)
   - **tags**: Relevant categories as an array ["Unit", "Component", etc.]
   - **steps**: An array of test steps, each containing:
     - **step_number**: The sequence number
     - **action**: The action to perform
     - **expected_result**: What should happen if test passes

### **OUTPUT FORMAT (JSON)**
```json
{
  "Unit_Tests": [
    {
      "test_id": "UNIT-001",
      "summary": "Verify button component renders correctly with different props",
      "priority": "P1",
      "tags": ["Unit", "Component", "Button"],
      "steps": [
        {
          "step_number": 1,
          "action": "Render button component with 'primary' variant prop",
          "expected_result": "Button renders with primary styling (background color, text color)"
        },
        {
          "step_number": 2,
          "action": "Render button component with 'disabled' prop set to true",
          "expected_result": "Button renders with disabled styling and cannot be clicked"
        },
        {
          "step_number": 3,
          "action": "Simulate click event on enabled button",
          "expected_result": "onClick handler is called exactly once"
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

    return {"Unit_Tests": test_cases}
