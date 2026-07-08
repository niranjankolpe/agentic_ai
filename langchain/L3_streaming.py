import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_ollama import ChatOllama
llm = ChatOllama(model="llama3.2:3b")


# Initialize your database connection
from langchain_community.utilities.sql_database import SQLDatabase
db = SQLDatabase.from_uri("sqlite:///Chinook.db")

from langchain.agents import create_agent

# create your agent! Add the model object you just created, a prompt etc.
agent = create_agent(
    model=llm,
    system_prompt="You are a full-stack comedian",
)

result = agent.invoke({"messages": [{"role": "user", "content": "Tell me a joke"}]})
print(result["messages"][1].content)

# Stream = values
for step in agent.stream(
    {"messages": [{"role": "user", "content": "Tell me a Dad joke"}]},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()

for token, metadata in agent.stream(
    {"messages": [{"role": "user", "content": "Write me a family friendly poem."}]},
    stream_mode="messages",
):
    print(f"{token.content}", end="")

from langchain.agents import create_agent
from langgraph.config import get_stream_writer


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    writer = get_stream_writer()
    # stream any arbitrary data
    writer(f"Looking up data for city: {city}")
    writer(f"Acquired data for city: {city}")
    return f"It's always sunny in {city}!"


agent = create_agent(
    model=llm,
    tools=[get_weather],
)

for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "What is the weather in SF?"}]},
    stream_mode=["values", "custom"],
):
    print(chunk)

for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "What is the weather in SF?"}]},
    stream_mode=["custom"],
):
    print(chunk)

for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "What is the weather in SF?"}]},
    stream_mode=["values", "custom"],
):
    if chunk[0] == "custom":
        print(chunk[1])