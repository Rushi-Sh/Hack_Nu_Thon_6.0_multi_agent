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
            "Analyze system performance and load-handling capabilities from the provided requirements document: {requirements_content}. "
            "Generate structured test cases covering:\n"
            "- **Load Testing**: Measure response time, throughput, and resource utilization under expected user loads.\n"
            "- **Stress Testing**: Simulate extreme traffic to test system limits and failure recovery mechanisms.\n"
            "- **Scalability Testing**: Evaluate system behavior when adding/removing resources (horizontal/vertical scaling).\n"
            "- **Concurrency & Bottleneck Analysis**: Identify thread locking, deadlocks, and synchronization issues.\n"
            "- **Latency & Network Performance**: Test API response times under different network conditions.\n"
            "- **Spike Testing**: Measure system resilience when handling sudden and unpredictable load spikes.\n"
            "- **Endurance Testing**: Assess system stability over prolonged periods of sustained load.\n"
        ),
    )

    chain = LLMChain(llm=groq_llm, prompt=prompt)
    test_cases = chain.run({"requirements_content": requirements_content})

    return {"Load_Tests": test_cases}
