import langgraph
from langchain.agents import AgentExecutor
from langgraph.graph import Graph, START, END
from .Layout_agent import generate_layout_tests
from .Accessibility_agent import generate_accessibility_tests
from .Responsiveness_agent import generate_responsiveness_tests
from .Usability_agent import generate_usability_tests

def uiux_pipeline(figma_json, website_content, requirements_content=None):
    """Executes UI/UX testing using LangGraph."""
    
    graph = Graph()
    
    graph.add_node("Visual_Consistency_Tests", generate_layout_tests)
    graph.add_node("Accessibility_Tests", generate_accessibility_tests)
    graph.add_node("Responsiveness_Tests", generate_responsiveness_tests)
    graph.add_node("Usability_Tests", generate_usability_tests)

    graph.add_edge(START, "Visual_Consistency_Tests")
    graph.add_edge("Visual_Consistency_Tests", "Accessibility_Tests")
    graph.add_edge("Accessibility_Tests", "Responsiveness_Tests")
    graph.add_edge("Responsiveness_Tests", "Usability_Tests")
    graph.add_edge("Usability_Tests", END)

    # Create a compiled graph that can be executed
    compiled_graph = graph.compile()
    return compiled_graph.invoke({"figma_json": figma_json, "website_content": website_content, "requirements_content": requirements_content})
