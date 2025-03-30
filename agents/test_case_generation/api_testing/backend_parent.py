import langgraph
from langchain.agents import AgentExecutor
from langgraph.graph import Graph, START, END
from .APITest_agent import generate_api_tests
from .BusinessLogic_agent import generate_business_logic_tests
from .DBTest_agent import generate_database_tests
from .SecurityTest_agent import generate_security_tests
from .LoadTest_agent import generate_load_tests

def backend_pipeline(requirements_content):
    """Executes Backend testing using LangGraph."""
    
    graph = Graph()
    
    graph.add_node("API_Tests", generate_api_tests)
    graph.add_node("Business_Logic_Tests", generate_business_logic_tests)
    graph.add_node("Database_Tests", generate_database_tests)
    graph.add_node("Security_Tests", generate_security_tests)
    graph.add_node("Load_Tests", generate_load_tests)

    graph.add_edge(START, "API_Tests")
    graph.add_edge("API_Tests", "Business_Logic_Tests")
    graph.add_edge("Business_Logic_Tests", "Database_Tests")
    graph.add_edge("Database_Tests", "Security_Tests")
    graph.add_edge("Security_Tests", "Load_Tests")
    graph.add_edge("Load_Tests", END)

    # Create a compiled graph that can be executed
    compiled_graph = graph.compile()
    return compiled_graph.invoke({"requirements_content": requirements_content})
