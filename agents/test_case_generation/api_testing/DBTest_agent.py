import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_database_tests(requirements_content):
    """Generates comprehensive database test cases for schema validation, query optimization, and data integrity."""
    
    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["requirements_content"],
        template=(
           """
           You are an expert in **Database Testing** for web applications.
Analyze the database schema and queries from the provided requirements document to generate structured database test cases.

### **INPUT DATA**
- **Database Requirements**:  
  {requirements_content}

### **TASK**
1. **Generate comprehensive database test cases** covering:  
   - **Schema Validation** (data types, constraints, relationships)
   - **Data Integrity & Consistency** (referential integrity, cascading operations)
   - **Indexing Efficiency** (clustered vs non-clustered indexing)
   - **Query Performance** (slow queries, join optimization, execution plans)
   - **Backup & Recovery** (backup mechanisms, restoration, disaster recovery)
   - **Concurrency & Transaction Handling** (isolation levels, deadlocks, rollbacks)
   - **Security & Access Control** (role-based access, encryption, SQL injection prevention)

2. **Each test case must include**:  
   - **test_id**: A unique identifier (e.g., "DB-001")
   - **summary**: Short description of what is being tested
   - **priority**: Importance level (P1, P2, P3)
   - **tags**: Relevant categories as an array ["Database", "Schema", etc.]
   - **steps**: An array of test steps, each containing:
     - **step_number**: The sequence number
     - **action**: The action to perform
     - **expected_result**: What should happen if test passes

### **OUTPUT FORMAT (JSON)**
```json
{
  "Database_Tests": [
    {
      "test_id": "DB-001",
      "summary": "Verify foreign key constraint enforcement",
      "priority": "P1",
      "tags": ["Database", "Integrity", "ForeignKey"],
      "steps": [
        {
          "step_number": 1,
          "action": "Attempt to delete a parent record with existing child records",
          "expected_result": null
        },
        {
          "step_number": 2,
          "action": "Verify database response",
          "expected_result": "Database rejects deletion with foreign key constraint violation error"
        },
        {
          "step_number": 3,
          "action": "Check that parent and child records remain intact",
          "expected_result": "All records exist unchanged in the database"
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

    return {"Database_Tests": test_cases}
