import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_business_logic_tests(requirements_content):
    """Generates backend business logic test cases, ensuring validation, rule enforcement, and transaction integrity."""
    
    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["requirements_content"],
        template=(
            """
            You are an expert in **Business Logic Testing** for backend applications.
Analyze the business logic from the provided requirements document to generate structured test cases.

### **INPUT DATA**
- **Business Requirements**:  
  {requirements_content}

### **TASK**
1. **Generate comprehensive business logic test cases** covering:  
   - **Business Rule Enforcement and Logic Consistency**
   - **Data Validation** (input validation, format checking, constraints)
   - **Workflow Correctness and Sequential Process Validation**
   - **Edge Cases and Exception Handling**
   - **Transaction Management** (ACID compliance, rollback, commit behavior)
   - **Dependency Validation** between different services/modules
   - **Calculation and Aggregation Logic**

2. **Each test case must include**:  
   - **test_id**: A unique identifier (e.g., "BL-001")
   - **summary**: Short description of what is being tested
   - **priority**: Importance level (P1, P2, P3)
   - **tags**: Relevant categories as an array ["Business Logic", "Validation", etc.]
   - **steps**: An array of test steps, each containing:
     - **step_number**: The sequence number
     - **action**: The action to perform
     - **expected_result**: What should happen if test passes

### **OUTPUT FORMAT (JSON)**
```json
{
  "Business_Logic_Tests": [
    {
      "test_id": "BL-001",
      "summary": "Verify discount calculation for premium customers",
      "priority": "P1",
      "tags": ["Business Logic", "Calculation", "Discount"],
      "steps": [
        {
          "step_number": 1,
          "action": "Create order with total amount of $1000 for a premium customer",
          "expected_result": null
        },
        {
          "step_number": 2,
          "action": "Trigger discount calculation logic",
          "expected_result": "System applies 15% discount as per premium customer rule"
        },
        {
          "step_number": 3,
          "action": "Verify final order amount",
          "expected_result": "Final amount is $850 ($1000 - 15%)"
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

    return {"Business_Logic_Tests": test_cases}
