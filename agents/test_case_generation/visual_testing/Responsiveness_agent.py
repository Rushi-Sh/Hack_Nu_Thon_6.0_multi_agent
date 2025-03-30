import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_responsiveness_tests(state):
    """
    Generates responsiveness test cases using Figma JSON and project requirements.
    Ensures UI adapts correctly to different screen sizes.
    """
    figma_json = state["figma_json"]
    requirements_content = state["requirements_content"]

    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["figma_json", "requirements_content"],
        template=(
           """
           You are an expert in **Responsiveness Testing** for web and mobile applications.
Analyze the UI design from **Figma JSON** and **project requirements** to generate structured responsiveness test cases.

### **INPUT DATA**
- **Figma UI Elements**:  
  {figma_json}
- **Software Requirements**:  
  {requirements_content}

### **TASK**
1. **Generate comprehensive responsiveness test cases** covering:  
   - **Mobile Resolutions** (375x667, 414x896, 390x844)
   - **Tablet Resolutions** (768x1024, 820x1180, 912x1368)
   - **Desktop Resolutions** (1280x720, 1440x900, 1920x1080)
   - **Layout Adjustments and Scaling**
   - **Grid/Flexbox Responsiveness**
   - **Text Wrapping and Truncation**
   - **Touch Gestures and Interactive Elements**
   - **Critical UI Element Visibility**  

2. **Each test case must include**:  
   - **test_id**: A unique identifier (e.g., "RES-001")
   - **summary**: Short description of what is being tested
   - **priority**: Importance level (P1, P2, P3)
   - **tags**: Relevant categories as an array ["Responsive", "Mobile", etc.]
   - **steps**: An array of test steps, each containing:
     - **step_number**: The sequence number
     - **action**: The action to perform
     - **expected_result**: What should happen if test passes

### **OUTPUT FORMAT (JSON)**
```json
{
  "Responsiveness_Tests": [
    {
      "test_id": "RES-001",
      "summary": "Verify layout adaptation on mobile devices",
      "priority": "P1",
      "tags": ["Responsive", "Mobile", "Layout"],
      "steps": [
        {
          "step_number": 1,
          "action": "Load the application on iPhone 12 resolution (390x844)",
          "expected_result": null
        },
        {
          "step_number": 2,
          "action": "Compare layout with design specifications",
          "expected_result": "UI elements properly stack and resize according to mobile design"
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

    return {"Responsiveness_Tests": test_cases}
