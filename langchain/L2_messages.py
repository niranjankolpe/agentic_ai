import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_community.utilities.sql_database import SQLDatabase

# Initialize your database connection
db = SQLDatabase.from_uri("sqlite:///Chinook.db")

from langchain_ollama import ChatOllama
llm = ChatOllama(model="llama3.2:3b")

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

# create your agent! Add the model object you just created, a prompt etc.
agent = create_agent(
    model=llm,
    system_prompt="You are a full-stack comedian"
)

# create a human message
human_msg = HumanMessage("Hello, how are you?")

# and invoke the agent with it!
result = agent.invoke({"messages": [human_msg]})

for msg in result["messages"]:
    print(f"{msg.type}: {msg.content}\n")


# Tool messages
from langchain_core.tools import tool

@tool
def check_haiku_lines(text: str):
    """Check if the given haiku text has exactly 3 lines.

    Returns None if it's correct, otherwise an error message.
    """
    # Split the text into lines, ignoring leading/trailing spaces
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    print(f"checking haiku, it has {len(lines)} lines:\n {text}")

    if len(lines) != 3:
        return f"Incorrect! This haiku has {len(lines)} lines. A haiku must have exactly 3 lines."
    return "Correct, this haiku has 3 lines."

agent = create_agent(
    model=llm,
    tools=[check_haiku_lines],
    system_prompt="You are a sports poet who only writes Haiku. You always check your work.",
)

result = agent.invoke({"messages": "Please write me a poem"})

for i, msg in enumerate(result["messages"]):
    msg.pretty_print()