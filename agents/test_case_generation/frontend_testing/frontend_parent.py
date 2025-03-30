import langgraph
from langgraph.graph import Graph, START, END
from .UnitTest_agent import generate_unit_tests
from .IntegrationTest_agent import generate_integration_tests
from .PerformanceTest_agent import generate_performance_tests
from .FunctionalTest_agent import generate_functional_tests

def frontend_pipeline(requirements_content, figma_json):
    state = {"requirements_content": requirements_content, "figma_json": figma_json}

    graph = Graph()
    
    graph.add_node("Unit_Tests", generate_unit_tests)
    graph.add_node("Functional_Tests", generate_functional_tests)
    graph.add_node("Integration_Tests", generate_integration_tests)
    graph.add_node("Performance_Tests", generate_performance_tests)

    graph.add_edge(START, "Unit_Tests")
    graph.add_edge("Unit_Tests", "Functional_Tests")
    graph.add_edge("Functional_Tests", "Integration_Tests")
    graph.add_edge("Integration_Tests", "Performance_Tests")
    graph.add_edge("Performance_Tests", END)

    compiled_graph = graph.compile()
    return compiled_graph.invoke(state)  # Ensure it gets a dictionary

