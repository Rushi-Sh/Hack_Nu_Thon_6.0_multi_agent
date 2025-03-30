import langgraph
from langgraph.graph import StateGraph, START, END
from typing import Annotated, TypedDict

# Import test generation functions
from .Layout_agent import generate_layout_tests
from .Accessibility_agent import generate_accessibility_tests
from .Responsiveness_agent import generate_responsiveness_tests
from .Usability_agent import generate_usability_tests

# Define State
class UIUXState(TypedDict):
    figma_json: dict
    requirements_content: str
    visual_tests: list
    accessibility_tests: list
    responsiveness_tests: list
    usability_tests: list

def uiux_pipeline(figma_json, requirements_content):
    """Executes UI/UX testing using LangGraph, based on Figma JSON and requirements content."""

    graph = StateGraph(UIUXState)

    # Nodes with correct state references
    graph.add_node("Visual_Consistency_Tests", lambda state: {
        "visual_tests": generate_layout_tests(state["figma_json"], state["requirements_content"])
    })
    graph.add_node("Accessibility_Tests", lambda state: {
        "accessibility_tests": generate_accessibility_tests(state["figma_json"], state["requirements_content"])
    })
    graph.add_node("Responsiveness_Tests", lambda state: {
        "responsiveness_tests": generate_responsiveness_tests(state["figma_json"], state["requirements_content"])
    })
    graph.add_node("Usability_Tests", lambda state: {
        "usability_tests": generate_usability_tests(state["figma_json"], state["requirements_content"])
    })

    # Defining execution flow
    graph.add_edge(START, "Visual_Consistency_Tests")
    graph.add_edge("Visual_Consistency_Tests", "Accessibility_Tests")
    graph.add_edge("Accessibility_Tests", "Responsiveness_Tests")
    graph.add_edge("Responsiveness_Tests", "Usability_Tests")
    graph.add_edge("Usability_Tests", END)

    # Compile and execute the graph
    compiled_graph = graph.compile()
    return compiled_graph.invoke({
        "figma_json": figma_json,
        "requirements_content": requirements_content
    })
