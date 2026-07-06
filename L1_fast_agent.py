from dataclasses import dataclass
from langchain_community.utilities.sql_database import SQLDatabase

# Initialize your database connection
db = SQLDatabase.from_uri("sqlite:///Chinook.db")

import warnings
warnings.filterwarnings("ignore")

# define context structure to support dependency injection
@dataclass
class RuntimeContext:
    db: SQLDatabase

from langchain_core.tools import tool
from langgraph.runtime import get_runtime

@tool
def execute_sql(query: str) -> str:
    """Execute a SQLite command and return results."""
    runtime = get_runtime(RuntimeContext)
    db = runtime.context.db

    try:
        return db.run(query)
    except Exception as e:
        return f"Error: {e}"
    
SYSTEM_PROMPT = """You are a careful SQLite analyst.

Rules:
- Think step-by-step.
- When you need data, call the tool `execute_sql` with ONE SELECT query.
- Read-only only; no INSERT/UPDATE/DELETE/ALTER/DROP/CREATE/REPLACE/TRUNCATE.
- Limit to 5 rows of output unless the user explicitly asks otherwise.
- If the tool returns 'Error:', revise the SQL and try again.
- Prefer explicit column lists; avoid SELECT *.
"""

# Deprecated
# from langchain.chat_models import init_chat_model
# odel = init_chat_model("ollama:llama3.2:3b", temperature=0)

from langchain_ollama import ChatOllama
llm = ChatOllama(model="llama3.2:3b")

from langchain.agents import create_agent

agent = create_agent(
    model=llm,
    tools=[execute_sql],
    system_prompt=SYSTEM_PROMPT,
    context_schema=RuntimeContext,
)

question = "Which table has the largest number of entries?"

for step in agent.stream(
    {"messages": question},
    context=RuntimeContext(db=db),
    stream_mode="values",
):
    step["messages"][-1].pretty_print()