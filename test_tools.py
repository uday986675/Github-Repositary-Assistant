from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from tools.find_file import find_file_tool
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
).bind_tools([find_file_tool])

response = llm.invoke(
    [HumanMessage(content="Find README.md")]
)

print(response)
print(response.tool_calls)