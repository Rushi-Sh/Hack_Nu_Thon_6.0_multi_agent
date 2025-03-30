import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_load_tests(requirements_content):
    """Generates backend load, stress, and scalability test cases."""
    
    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["requirements_content"],
        template=(
          """
          You are an expert in **Load Testing** for backend systems.
Analyze system performance and load-handling capabilities from the provided requirements document to generate structured test cases.

### **INPUT DATA**
- **Performance Requirements**:  
  {requirements_content}

### **TASK**
1. **Generate comprehensive load and performance test cases** covering:  
   - **Load Testing** (response time, throughput, resource utilization)
   - **Stress Testing** (system limits, failure recovery mechanisms)
   - **Scalability Testing** (horizontal/vertical scaling behavior)
   - **Concurrency & Bottleneck Analysis** (thread locking, deadlocks)
   - **Latency & Network Performance** (API response times, network conditions)
   - **Spike Testing** (sudden and unpredictable load spikes)
   - **Endurance Testing** (stability over prolonged periods)

2. **Each test case must include**:  
   - **test_id**: A unique identifier (e.g., "LOAD-001")
   - **summary**: Short description of what is being tested
   - **priority**: Importance level (P1, P2, P3)
   - **tags**: Relevant categories as an array ["Load", "Performance", etc.]
   - **steps**: An array of test steps, each containing:
     - **step_number**: The sequence number
     - **action**: The action to perform
     - **expected_result**: What should happen if test passes

### **OUTPUT FORMAT (JSON)**
```json
{
  "Load_Tests": [
    {
      "test_id": "LOAD-001",
      "summary": "Verify system performance under normal user load",
      "priority": "P1",
      "tags": ["Load", "Performance", "Baseline"],
      "steps": [
        {
          "step_number": 1,
          "action": "Simulate 500 concurrent users performing standard operations",
          "expected_result": null
        },
        {
          "step_number": 2,
          "action": "Monitor response times for critical transactions",
          "expected_result": "Average response time under 1.5 seconds for all transactions"
        },
        {
          "step_number": 3,
          "action": "Check server resource utilization",
          "expected_result": "CPU usage below 70%, memory usage below 80%"
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

    return {"Load_Tests": test_cases}
