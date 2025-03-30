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
            "Analyze the business logic from the provided requirements document: {requirements_content}. "
            "Generate backend test cases focusing on:\n"
            "- Business rule enforcement and logic consistency\n"
            "- Data validation (input validation, format checking, constraints, etc.)\n"
            "- Workflow correctness and sequential process validation\n"
            "- Edge cases and exception handling\n"
            "- Transaction management (ACID compliance, rollback, commit behavior)\n"
            "- Dependency validation between different services/modules"
        ),
    )

    chain = LLMChain(llm=groq_llm, prompt=prompt)
    test_cases = chain.run({"requirements_content": requirements_content})

    return {"Business_Logic_Tests": test_cases}
