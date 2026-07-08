import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_ollama import ChatOllama
llm = ChatOllama(model="llama3.2:3b")


# Initialize your database connection
from langchain_community.utilities.sql_database import SQLDatabase
db = SQLDatabase.from_uri("sqlite:///Chinook.db")

from typing import Literal

from langchain.tools import tool


@tool
def real_number_calculator(
    a: float, b: float, operation: Literal["add", "subtract", "multiply", "divide"]
) -> float:
    """Perform basic arithmetic operations on two real numbers."""
    print(" Invoking calculator tool")
    # Perform the specified operation
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            raise ValueError("Division by zero is not allowed.")
        return a / b
    else:
        raise ValueError(f"Invalid operation: {operation}")
    
from langchain.agents import create_agent

agent = create_agent(
    model=llm,
    tools=[real_number_calculator],
    system_prompt="You are a helpful assistant",
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "what is 3.1125 * 4.1234"}]}
)
print(result["messages"][-1].content)

result = agent.invoke({"messages": [{"role": "user", "content": "what is 3 * 4"}]})
print(result["messages"][-1].content)

result = agent.invoke({"messages": [{"role": "user", "content": "what is 3.0 * 4.0"}]})
print(result["messages"][-1].content)


# Add more detailed description
from typing import Literal

from langchain.tools import tool


@tool(
    "calculator",
    parse_docstring=True,
    description=(
        "Perform basic arithmetic operations on two real numbers."
        "Use this whenever you have operations on any numbers, even if they are integers."
    ),
)
def real_number_calculator(
    a: float, b: float, operation: Literal["add", "subtract", "multiply", "divide"]
) -> float:
    """Perform basic arithmetic operations on two real numbers.

    Args:
        a (float): The first number.
        b (float): The second number.
        operation (Literal["add", "subtract", "multiply", "divide"]):
            The arithmetic operation to perform.

            - `"add"`: Returns the sum of `a` and `b`.
            - `"subtract"`: Returns the result of `a - b`.
            - `"multiply"`: Returns the product of `a` and `b`.
            - `"divide"`: Returns the result of `a / b`. Raises an error if `b` is zero.

    Returns:
        float: The numerical result of the specified operation.

    Raises:
        ValueError: If an invalid operation is provided or division by zero is attempted.
    """
    print("Invoking calculator tool")
    # Perform the specified operation
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            raise ValueError("Division by zero is not allowed.")
        return a / b
    else:
        raise ValueError(f"Invalid operation: {operation}")
    
from langchain.agents import create_agent

agent = create_agent(
    model=llm,
    tools=[real_number_calculator],
    system_prompt="You are a helpful assistant",
)

result = agent.invoke({"messages": [{"role": "user", "content": "what is 3.0 * 4.0"}]})
print(result["messages"][-1].content)

result = agent.invoke({"messages": [{"role": "user", "content": "what is 3 * 4"}]})
print(result["messages"][-1].content)

# Create your own tool

@tool
def your_tool(
    a: float, b: float, 
) -> float:
    """Perform your favorite operation

    Args:
        a (float): operator a description
        b (float): operator b description

    Returns:
        float: description
    """
    pass

from langchain.agents import create_agent

agent = create_agent(
    model=llm,
    tools=[your_tool],
    system_prompt="You are a helpful assistant",
)