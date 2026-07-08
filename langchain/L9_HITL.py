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

Here is the exact database schema. Use ONLY these exact table and column names:
{schema}

Rules:
- Think step-by-step.
- When you need data, call the tool `execute_sql` with ONE SELECT query.
- Read-only only; no INSERT/UPDATE/DELETE/ALTER/DROP/CREATE/REPLACE/TRUNCATE.
- Limit to 5 rows unless the user explicitly asks otherwise.
- If the tool returns 'Error:', revise the SQL and try again.
- Only use table and column names that exist in the schema above.
- Prefer explicit column lists; avoid SELECT *.
- If the database is offline, ask user to try again later without further comment.
- Report only the columns returned. Do not add names not in the result.
""".format(schema=db.get_table_info())

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(
    model=llm,
    tools=[execute_sql],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=InMemorySaver(),
    context_schema=RuntimeContext,
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={"execute_sql": {"allowed_decisions": ["approve", "reject"]}},
        ),
    ],
)

from langgraph.types import Command

question = "What are the names of all the employees?"

config = {"configurable": {"thread_id": "1"}}

result = agent.invoke(
    {"messages": [{"role": "user", "content": question}]},
    config=config,
    context=RuntimeContext(db=db)
)

if "__interrupt__" in result:
    description = result['__interrupt__'][-1].value['action_requests'][-1]['description']
    print(f"\033[1;3;31m{80 * '-'}\033[0m")
    print(
        f"\033[1;3;31m Interrupt:{description}\033[0m"
    )

    result = agent.invoke(
        Command(
            resume={
                "decisions": [{"type": "reject", "message": "the database is offline."}]
            }
        ),
        config=config,  # Same thread ID to resume the paused conversation
        context=RuntimeContext(db=db),
    )
    print(f"\033[1;3;31m{80 * '-'}\033[0m")

print(result["messages"][-1].content)

config = {"configurable": {"thread_id": "2"}}

result = agent.invoke(
    {"messages": [{"role": "user", "content": question}]},
    config=config,
    context=RuntimeContext(db=db)
)

while "__interrupt__" in result:
    description = result['__interrupt__'][-1].value['action_requests'][-1]['description']
    print(f"\033[1;3;31m{80 * '-'}\033[0m")
    print(
        f"\033[1;3;31m Interrupt:{description}\033[0m"
    )
    
    result = agent.invoke(
        Command(
            resume={"decisions": [{"type": "approve"}]}
        ),
        config=config,  # Same thread ID to resume the paused conversation
        context=RuntimeContext(db=db),
    )

for msg in result["messages"]:
    msg.pretty_print()