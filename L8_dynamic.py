import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_ollama import ChatOllama
llm = ChatOllama(model="llama3.2:3b")

from langchain_community.utilities.sql_database import SQLDatabase
db = SQLDatabase.from_uri("sqlite:///Chinook.db")
schema_info = db.get_table_info()

from dataclasses import dataclass

@dataclass
class RuntimeContext:
    is_employee: bool
    db: SQLDatabase

from langchain_core.tools import tool
from langgraph.runtime import get_runtime

@tool
def execute_sql(query: str) -> str:
    """Execute a SQLite command and return results."""
    runtime = get_runtime(RuntimeContext)
    db = runtime.context.db

    if not runtime.context.is_employee:
        blocked = ["Customer", "Invoice", "InvoiceLine", "Employee"]
        if any(t.upper() in query.upper() for t in blocked):
            return "Access denied: you do not have permission to query this table."

    try:
        result = db.run(query)
        return str(result)[:20]   # cap output size
    except Exception as e:
        return f"Error: {e}"

SYSTEM_PROMPT_TEMPLATE = """You are a careful SQLite analyst.

Here is the exact database schema:
{schema_info}

Rules:
- Think step-by-step.
- When you need data, call the tool `execute_sql` with ONE SELECT query.
- Read-only only; no INSERT/UPDATE/DELETE/ALTER/DROP/CREATE/REPLACE/TRUNCATE.
- Limit to 5 rows unless the user explicitly asks otherwise.
{table_limits}
- If the tool returns 'Error:', revise the SQL and try again.
- If the tool returns 'Access denied', you MUST stop and reply with exactly that denial message. Do NOT invent, guess, or list any data.
- Never fabricate data. Only report what the tool actually returned.
- Only use columns that exist in the schema above.
- Prefer explicit column lists; avoid SELECT *.
"""

from langchain.agents.middleware.types import ModelRequest, dynamic_prompt

@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest) -> str:
    if not request.runtime.context.is_employee:
        table_limits = "- Limit access to these tables: Album, Artist, Genre, Playlist, PlaylistTrack, Track."
    else:
        table_limits = ""

    return SYSTEM_PROMPT_TEMPLATE.format(
        schema_info=schema_info,
        table_limits=table_limits
    )

from langchain.agents import create_agent

agent = create_agent(
    model=llm,
    tools=[execute_sql],
    middleware=[dynamic_system_prompt],
    context_schema=RuntimeContext,
)

question = "List all customers and their email addresses."

for step in agent.stream(
    {"messages": [{"role": "user", "content": question}]},
    context=RuntimeContext(is_employee=False, db=db),
    stream_mode="values",
):
    step["messages"][-1].pretty_print()

for step in agent.stream(
    {"messages": [{"role": "user", "content": question}]},
    context=RuntimeContext(is_employee=True, db=db),
    stream_mode="values",
):
    step["messages"][-1].pretty_print()