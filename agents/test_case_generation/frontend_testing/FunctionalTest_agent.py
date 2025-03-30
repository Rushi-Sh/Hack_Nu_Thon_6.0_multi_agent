import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_functional_tests(state):
    """Generates functional UI test cases for buttons, forms, and interactive elements."""
    figma_json = state["figma_json"]
    requirements_content = state["requirements_content"]
    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["figma_json", "requirements_content"],
        template=(
           """
           You are an expert in **Functional Testing** for frontend applications.
Analyze UI functionalities from **Figma JSON** and **user requirements** to generate structured functional test cases.

### **INPUT DATA**
- **Figma UI Elements**:  
  {figma_json}
- **Software Requirements**:  
  {requirements_content}

### **TASK**
1. **Generate comprehensive functional test cases** covering:  
   - **Button Interactions** (click events, state changes)
   - **Form Submissions** (data capture, validation, submission)
   - **Modal Dialogues** (opening, closing, data persistence)
   - **Dropdown Menus** (selection, filtering, multi-select behavior)
   - **Error Handling** (client-side validation, error messages)
   - **Interactive Elements** (sliders, toggles, checkboxes, radio buttons)
   - **State Management** (component states across user interactions)

2. **Each test case must include**:  
   - **test_id**: A unique identifier (e.g., "FUNC-001")
   - **summary**: Short description of what is being tested
   - **priority**: Importance level (P1, P2, P3)
   - **tags**: Relevant categories as an array ["Functional", "Button", etc.]
   - **steps**: An array of test steps, each containing:
     - **step_number**: The sequence number
     - **action**: The action to perform
     - **expected_result**: What should happen if test passes

### **OUTPUT FORMAT (JSON)**
```json
{
  "Functional_Tests": [
    {
      "test_id": "FUNC-001",
      "summary": "Verify form submission with valid inputs",
      "priority": "P1",
      "tags": ["Functional", "Form", "Validation"],
      "steps": [
        {
          "step_number": 1,
          "action": "Navigate to the form page",
          "expected_result": null
        },
        {
          "step_number": 2,
          "action": "Enter valid data into all required fields",
          "expected_result": "No validation errors are displayed"
        },
        {
          "step_number": 3,
          "action": "Click the submit button",
          "expected_result": "Form submits successfully and confirmation message appears"
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

    return {"Functional_Tests": test_cases}
