from IPython.display import Image, display
import operator
from typing import Annotated, Literal, TypedDict
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

import os

class State(TypedDict):
    nlist: list[str]

def node_a(state: State) -> State:
    print(f"node a is receiving {state['nlist']}")
    note = "Hello World from Node a"
    return(State(nlist = [note]))

builder = StateGraph(State)
builder.add_node("a", node_a)
builder.add_edge(START, "a")
builder.add_edge("a", END)
graph = builder.compile()

# display(Image(graph.get_graph().draw_mermaid_png()))
# print(graph.get_graph().draw_mermaid())

os.makedirs("output", exist_ok=True)
png = graph.get_graph().draw_mermaid_png()
with open("output/graph.png", "wb") as f:
    f.write(png)
print("Graph saved to output/graph.png")

initial_state = State(
    nlist = ["Hello Node a, how are you?"]
)
graph.invoke(initial_state)