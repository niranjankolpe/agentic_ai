import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_ollama import ChatOllama
llm = ChatOllama(model="llama3.2:3b")


# Initialize your database connection
from langchain_community.utilities.sql_database import SQLDatabase
db = SQLDatabase.from_uri("sqlite:///Chinook.db")

from typing_extensions import TypedDict
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy  

class ContactInfo(TypedDict):
    name: str
    email: str
    phone: str


# if the model provider (e.g. OpenAI) offers native support for structured
# output, use the ContactInfo class directly as the response format. Otherwise,
# use the ToolStrategy wrapper to enable structured output parsing for providers
# that don't have native support.
response_format = (
    ContactInfo if "openai" in llm._llm_type else ToolStrategy(ContactInfo)
)

agent = create_agent(model=llm, response_format=response_format)

recorded_conversation = """We talked with John Doe. He works over at Example. His number is, let's see, 
five, five, five, one two three, four, five, six seven. Did you get that?
And, his email was john at example.com. He wanted to order 50 boxes of Captain Crunch."""

result = agent.invoke(
    {"messages": [{"role": "user", "content": recorded_conversation}]}
)

print(result["structured_response"])

# Multi data types
from langchain.agents import create_agent
from pydantic import BaseModel
from langchain.agents.structured_output import ToolStrategy

class ContactInfo(BaseModel):
    name: str
    email: str
    phone: str


# if the model provider (e.g. OpenAI) offers native support for structured
# output, use the ContactInfo class directly as the response format. Otherwise,
# use the ToolStrategy wrapper to enable structured output parsing for providers
# that don't have native support.
response_format = (
    ContactInfo if "openai" in llm._llm_type else ToolStrategy(ContactInfo)
)

agent = create_agent(model=llm, response_format=response_format)

recorded_conversation = """ We talked with John Doe. He works over at Example. His number is, let's see, 
five, five, five, one two three, four, five, six seven. Did you get that?
And, his email was john at example.com. He wanted to order 50 boxes of Captain Crunch."""

result = agent.invoke(
    {"messages": [{"role": "user", "content": recorded_conversation}]}
)

print(result["structured_response"])