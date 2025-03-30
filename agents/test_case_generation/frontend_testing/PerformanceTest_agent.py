import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_performance_tests(state):
    """Generates test cases to measure frontend performance (load time, rendering speed, etc.)."""
    figma_json = state["figma_json"]
    requirements_content = state["requirements_content"]
    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["figma_json", "requirements_content"],
        template=(
           """
           You are an expert in **Performance Testing** for web applications.
Analyze UI elements from **Figma JSON** and **user requirements** to generate structured performance test cases.

### **INPUT DATA**
- **Figma UI Elements**:  
  {figma_json}
- **Software Requirements**:  
  {requirements_content}

### **TASK**
1. **Generate comprehensive performance test cases** covering:  
   - **Page Load Times** (initial load, subsequent navigations)
   - **Rendering Delays** (time to first meaningful paint)
   - **Lazy Loading Efficiency** (images, components, resources)
   - **Script Execution Speed** (JavaScript performance)
   - **Memory Usage** (leak detection, resource management)
   - **Browser Compatibility** (cross-browser performance)
   - **Animation Smoothness** (frames per second, jank)
   - **Network Resource Optimization** (bundle size, request count)

2. **Each test case must include**:  
   - **test_id**: A unique identifier (e.g., "PERF-001")
   - **summary**: Short description of what is being tested
   - **priority**: Importance level (P1, P2, P3)
   - **tags**: Relevant categories as an array ["Performance", "LoadTime", etc.]
   - **steps**: An array of test steps, each containing:
     - **step_number**: The sequence number
     - **action**: The action to perform
     - **expected_result**: What should happen if test passes

### **OUTPUT FORMAT (JSON)**
```json
{
  "Performance_Tests": [
    {
      "test_id": "PERF-001",
      "summary": "Measure initial page load time across devices",
      "priority": "P1",
      "tags": ["Performance", "LoadTime", "Initial"],
      "steps": [
        {
          "step_number": 1,
          "action": "Use performance timing API to measure DOMContentLoaded event",
          "expected_result": null
        },
        {
          "step_number": 2,
          "action": "Record time from navigation start to interactive",
          "expected_result": "Page loads within 3 seconds on desktop and 5 seconds on mobile"
        },
        {
          "step_number": 3,
          "action": "Examine network waterfall",
          "expected_result": "Critical resources are prioritized and loaded first"
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

    return {"Performance_Tests": test_cases}
