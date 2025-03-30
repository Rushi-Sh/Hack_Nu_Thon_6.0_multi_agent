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
            "Analyze the database schema and queries from the provided requirements document: {requirements_content}. "
            "Generate structured database test cases covering:\n"
            "- **Schema Validation**: Ensure correct data types, constraints (PK, FK, NOT NULL, UNIQUE, CHECK), and relationships.\n"
            "- **Data Integrity & Consistency**: Validate referential integrity, cascading operations, and ACID compliance.\n"
            "- **Indexing Efficiency**: Test index performance, covering clustered vs non-clustered indexing.\n"
            "- **Query Performance**: Benchmark slow queries, optimize joins, and analyze query execution plans.\n"
            "- **Backup & Recovery**: Test database backup mechanisms, restoration, and disaster recovery readiness.\n"
            "- **Concurrency & Transaction Handling**: Validate isolation levels, deadlock scenarios, and rollback behavior.\n"
            "- **Security & Access Control**: Ensure role-based access control, encryption, and SQL injection prevention.\n"
        ),
    )

    chain = LLMChain(llm=groq_llm, prompt=prompt)
    test_cases = chain.run({"requirements_content": requirements_content})

    return {"Database_Tests": test_cases}
