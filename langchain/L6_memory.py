import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

llm = ChatOllama(model="llama3.2:3b")

memory = MemorySaver()

agent = create_agent(
    model=llm,
    system_prompt="You are a helpful assistant",
    checkpointer=memory,
)

config = {"configurable": {"thread_id": "demo-thread"}}

# Turn 1
for step in agent.stream(
    {"messages": [{"role": "user", "content": "My name is Steven Rogers"}]},
    config=config,
    stream_mode="values",
):
    step["messages"][-1].pretty_print()

# Turn 2 — tests if agent remembers
for step in agent.stream(
    {"messages": [{"role": "user", "content": "What is my name?"}]},
    config=config,
    stream_mode="values",
):
    step["messages"][-1].pretty_print()