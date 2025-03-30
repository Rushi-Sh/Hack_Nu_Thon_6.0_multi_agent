import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_security_tests(requirements_content):
    """Generates comprehensive backend security test cases for vulnerability assessment."""

    groq_llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    prompt = PromptTemplate(
        input_variables=["requirements_content"],
        template=(
            """
            You are an expert in **Security Testing** for backend systems.
Analyze backend security controls and potential risks based on the provided requirements document to generate structured security test cases.

### **INPUT DATA**
- **Security Requirements**:  
  {requirements_content}

### **TASK**
1. **Generate comprehensive security test cases** covering:  
   - **Authentication & Authorization** (login mechanisms, MFA, OAuth, access control)
   - **Session Security** (expiration, fixation, hijacking, CSRF protection)
   - **Injection Attacks** (SQL, NoSQL, command, LDAP injection)
   - **Cross-Site Scripting (XSS) & Cross-Site Request Forgery (CSRF)**
   - **API Security** (token management, rate limiting, CORS policies)
   - **Data Encryption & Storage** (password hashing, TLS enforcement)
   - **Server & Infrastructure Security** (configurations, open ports)
   - **Denial-of-Service (DoS) & Rate Limiting**
   - **Third-Party Dependency & Supply Chain Security**
   - **Security Headers & Policies** (CSP, HSTS)

2. **Each test case must include**:  
   - **test_id**: A unique identifier (e.g., "SEC-001")
   - **summary**: Short description of what is being tested
   - **priority**: Importance level (P1, P2, P3)
   - **tags**: Relevant categories as an array ["Security", "Authentication", etc.]
   - **steps**: An array of test steps, each containing:
     - **step_number**: The sequence number
     - **action**: The action to perform
     - **expected_result**: What should happen if test passes

### **OUTPUT FORMAT (JSON)**
```json
{
  "Security_Tests": [
    {
      "test_id": "SEC-001",
      "summary": "Verify protection against SQL injection attacks",
      "priority": "P1",
      "tags": ["Security", "Injection", "SQLi"],
      "steps": [
        {
          "step_number": 1,
          "action": "Identify input fields that interact with the database",
          "expected_result": null
        },
        {
          "step_number": 2,
          "action": "Attempt SQL injection payloads in login form ('OR 1=1--)",
          "expected_result": "System rejects input and does not authenticate user"
        },
        {
          "step_number": 3,
          "action": "Review database logs",
          "expected_result": "Attack attempt is logged with appropriate details"
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

    return {"Security_Tests": test_cases}
