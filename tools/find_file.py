from langchain_core.tools import tool
from .file_utils import find_file

@tool
def find_file_tool(file_name: str) -> str:
    """
    Find the location of a file.

    Use this tool only if the user wants to locate a file.
    """
    matches = find_file(file_name)

    if not matches:
        return "No matching files found."

    return "\n".join(matches)