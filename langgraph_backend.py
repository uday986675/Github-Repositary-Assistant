from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated
import re
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.prebuilt import tools_condition, ToolNode
from tools.find_file import find_file_tool
from tools.read_file import read_file
from tools.list_files import list_files
from tools.answer_repository_question import answer_repository_question
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT


load_dotenv()

tools = [find_file_tool, read_file, answer_repository_question, list_files]

base_model = ChatGoogleGenerativeAI(model = "gemini-3.5-flash")
tool_model = base_model.bind_tools(tools)

# for tool in tools:
#     print(tool.name)
#     print(tool.args)


FILE_NAME_PATTERN = re.compile(
    r"\b([A-Za-z0-9_.-]+\.(?:py|md|txt|json|ya?ml|toml|ini|cfg|env|csv|ipynb|js|ts|tsx|jsx|html|css|scss|sh|bat|ps1))\b",
    re.IGNORECASE,
)
SPECIAL_FILENAMES = {
    "dockerfile": "Dockerfile",
    "makefile": "Makefile",
    "license": "LICENSE",
    "readme": "README.md",
}


def extract_requested_file_name(text: str) -> str | None:
    lowered = text.lower()

    for needle, file_name in SPECIAL_FILENAMES.items():
        if needle in lowered:
            return file_name

    match = FILE_NAME_PATTERN.search(text)
    if match:
        return match.group(1)

    return None


def is_location_request(text: str) -> bool:
    lowered = text.lower()
    return any(
        phrase in lowered
        for phrase in ["where is", "locate", "find ", "path of", "file location"]
    )


def is_file_content_request(text: str) -> bool:
    lowered = text.lower()
    return any(
        phrase in lowered
        for phrase in [
            "show me",
            "show the",
            "show ",
            "display",
            "print",
            "read",
            "open",
            "give me",
            "what does",
            "what is inside",
            "contents of",
        ]
    )

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chatbot(state: State):
    print("=" * 80)
    print("STATE:")
    print(state)

    last_message = state["messages"][-1] if state["messages"] else None
    if isinstance(last_message, ToolMessage):
        if last_message.name == "read_file":
            return {"messages": [AIMessage(content=last_message.content)]}
        
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        response = tool_model.invoke(messages)
        return {"messages": [response]}
    elif isinstance(last_message, HumanMessage):
        user_text = str(last_message.content)
        requested_file = extract_requested_file_name(user_text)

        if requested_file and is_location_request(user_text):
            return {"messages": [AIMessage(content=find_file_tool.invoke({"file_name": requested_file}))]}

        if requested_file and is_file_content_request(user_text):
            return {"messages": [AIMessage(content=read_file.invoke({"file_name": requested_file}))]}

        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        model = tool_model
    else:
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        model = tool_model

    print("\nMESSAGES SENT TO MODEL:")
    for msg in messages:
        print(type(msg).__name__, ":", msg)

    response = model.invoke(messages)

    print("\nMODEL RESPONSE:")
    print(response)
    print("TOOL CALLS:", response.tool_calls)

    return {"messages": [response]}


graph = StateGraph(State)

# add nodes
graph.add_node("chatbot", chatbot)
graph.add_node("tools", ToolNode(tools))

# add edges
graph.add_edge(START, "chatbot")
graph.add_conditional_edges("chatbot", tools_condition)
graph.add_edge("tools", "chatbot")

workflow = graph.compile()

# for tool in tools:
#     print(tool.name)
#     print(tool.args)

# import langchain
# import langchain_core
# import langgraph
# import langchain_groq
# import groq

# from importlib.metadata import version

# print("langchain:", version('langchain'))
# print("langchain_core:", version('langchain-core'))
# print("langgraph:", version('langgraph'))
# print("langchain_groq:", version('langchain-groq'))
# print("groq:", version('groq'))
# print("pydantic:", version('pydantic'))