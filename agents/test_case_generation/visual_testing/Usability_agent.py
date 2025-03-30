import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_usability_tests(state):
    """
    Generates usability test cases based on UI design from Figma JSON
    and user requirements from the provided document.
    """
    figma_json = state["figma_json"]
    requirements_content = state["requirements_content"]

    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["figma_json", "requirements_content"],
        template=(
           """
           You are an expert in **Usability Testing** for software applications.
Analyze UI usability based on design elements from **Figma JSON** and **user requirements** to generate structured usability test cases.

### **INPUT DATA**
- **Figma UI Elements**:  
  {figma_json}
- **Software Requirements**:  
  {requirements_content}

### **TASK**
1. **Generate comprehensive usability test cases** covering:  
   - **Intuitive Navigation** (clear menus and interactive elements)
   - **User Feedback** (errors, actions, confirmations)
   - **Call-to-Action (CTA) Visibility and Accessibility**
   - **Error Prevention** (input validation, undo options)
   - **Cognitive Load Optimization**
   - **Usability Heuristics Compliance**  

2. **Each test case must include**:  
   - **test_id**: A unique identifier (e.g., "USE-001")
   - **summary**: Short description of what is being tested
   - **priority**: Importance level (P1, P2, P3)
   - **tags**: Relevant categories as an array ["Usability", "Navigation", etc.]
   - **steps**: An array of test steps, each containing:
     - **step_number**: The sequence number
     - **action**: The action to perform
     - **expected_result**: What should happen if test passes

### **OUTPUT FORMAT (JSON)**
```json
{
  "Usability_Tests": [
    {
      "test_id": "USE-001",
      "summary": "Verify navigation menu intuitiveness",
      "priority": "P1",
      "tags": ["Usability", "Navigation", "Menu"],
      "steps": [
        {
          "step_number": 1,
          "action": "Load the application and locate main navigation",
          "expected_result": null
        },
        {
          "step_number": 2,
          "action": "Examine menu structure and organization",
          "expected_result": "Navigation options are clearly labeled and organized in logical categories"
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

    return {"Usability_Tests": test_cases}
