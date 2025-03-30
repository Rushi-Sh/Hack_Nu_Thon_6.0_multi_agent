import langgraph
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

# Import test generation functions
from .APITest_agent import generate_api_tests
from .BusinessLogic_agent import generate_business_logic_tests
from .DBTest_agent import generate_database_tests
from .SecurityTest_agent import generate_security_tests
from .LoadTest_agent import generate_load_tests

# Define State
class BackendState(TypedDict):
    requirements_content: str
    api_tests: list
    business_logic_tests: list
    database_tests: list
    security_tests: list
    load_tests: list

def backend_pipeline(requirements_content):
    """Executes Backend testing pipeline using LangGraph."""
    
    graph = StateGraph(BackendState)

    # Add nodes for backend testing steps
    graph.add_node("API_Tests", lambda state: {
        "api_tests": generate_api_tests(state["requirements_content"])
    })
    graph.add_node("Business_Logic_Tests", lambda state: {
        "business_logic_tests": generate_business_logic_tests(state["requirements_content"])
    })
    graph.add_node("Database_Tests", lambda state: {
        "database_tests": generate_database_tests(state["requirements_content"])
    })
    graph.add_node("Security_Tests", lambda state: {
        "security_tests": generate_security_tests(state["requirements_content"])
    })
    graph.add_node("Load_Tests", lambda state: {
        "load_tests": generate_load_tests(state["requirements_content"])
    })

    # Define execution order
    graph.add_edge(START, "API_Tests")
    graph.add_edge("API_Tests", "Business_Logic_Tests")
    graph.add_edge("Business_Logic_Tests", "Database_Tests")
    graph.add_edge("Database_Tests", "Security_Tests")
    graph.add_edge("Security_Tests", "Load_Tests")
    graph.add_edge("Load_Tests", END)

    # Compile and execute the graph
    compiled_graph = graph.compile()
    return compiled_graph.invoke({"requirements_content": requirements_content})
