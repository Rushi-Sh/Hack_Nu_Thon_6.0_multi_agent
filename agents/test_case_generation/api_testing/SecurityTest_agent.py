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
            "Analyze backend security controls and potential risks based on the provided requirements document: {requirements_content}. "
            "Generate structured test cases covering:\n"
            "- **Authentication & Authorization**: Test login mechanisms, multi-factor authentication (MFA), OAuth, and access control enforcement.\n"
            "- **Session Security**: Validate session expiration, fixation, hijacking, and CSRF protection.\n"
            "- **Injection Attacks**: Detect SQL injection, NoSQL injection, command injection, and LDAP injection vulnerabilities.\n"
            "- **Cross-Site Scripting (XSS) & Cross-Site Request Forgery (CSRF)**: Test for stored, reflected, and DOM-based XSS, and validate CSRF token implementation.\n"
            "- **API Security**: Assess API token management, rate limiting, CORS policies, and broken object-level authorization (BOLA) issues.\n"
            "- **Data Encryption & Storage**: Verify password hashing, TLS enforcement, and exposure of sensitive data.\n"
            "- **Server & Infrastructure Security**: Identify misconfigurations, open ports, default credentials, and logging vulnerabilities.\n"
            "- **Denial-of-Service (DoS) & Rate Limiting**: Simulate high-traffic scenarios to test rate limiting and DoS resilience.\n"
            "- **Third-Party Dependency & Supply Chain Security**: Evaluate vulnerabilities in third-party packages and libraries.\n"
            "- **Security Headers & Policies**: Check HTTP security headers, Content Security Policy (CSP), and HSTS enforcement.\n"
        ),
    )

    chain = LLMChain(llm=groq_llm, prompt=prompt)
    test_cases = chain.run({"requirements_content": requirements_content})

    return {"Security_Tests": test_cases}
