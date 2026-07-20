from langchain_groq import ChatGroq
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

@tool
def answer_repository_question(question: str):
    """Answer repository questions."""
    return "dummy"

model = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

model = model.bind_tools([answer_repository_question])

response = model.invoke(
    "Which file contains the frontend part?"
)

print(response)
print(response.tool_calls)