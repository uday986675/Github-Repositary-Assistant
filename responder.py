import os
import streamlit as st
from dotenv import load_dotenv
from typing import Literal, TypedDict

load_dotenv()

st.set_page_config(
    page_title="GitHub Repository Assistant",
    page_icon="🤖",
    layout="wide"
)

# --- Imports for pipeline ---
from clone_url import clone_url
from parse_files import file_parser
from chunks_splitter import chunks_splitter
from database import create_database
from langgraph_backend import (
    workflow,
    State,
    extract_requested_file_name,
    is_file_content_request,
)


class AssistantResponse(TypedDict):
    content: str
    render_mode: Literal["markdown", "code"]
    language: str | None


def process_repository(repo_url: str):
    """Clone, parse, chunk, and build vector database from a GitHub repo."""
    with st.status("🔄 Processing repository...", expanded=True) as status:
        st.write("📥 Cloning repository...")
        try:
            clone_url(repo_url)
            st.write("✅ Repository cloned successfully")
        except Exception as e:
            st.error(f"❌ Failed to clone repository: {e}")
            return False

        st.write("📄 Parsing files...")
        try:
            documents = file_parser()
            st.write(f"✅ Parsed {len(documents)} documents")
        except Exception as e:
            st.error(f"❌ Failed to parse files: {e}")
            return False

        st.write("✂️ Splitting into chunks...")
        try:
            chunks = chunks_splitter(documents)
            st.write(f"✅ Created {len(chunks)} chunks")
        except Exception as e:
            st.error(f"❌ Failed to split chunks: {e}")
            return False

        st.write("🧠 Building vector database...")
        try:
            create_database(chunks)
            st.write("✅ Vector database built successfully")
        except Exception as e:
            st.error(f"❌ Failed to build database: {e}")
            return False

        status.update(label="✅ Repository processed successfully!", state="complete")

    return True


from langchain_core.messages import HumanMessage

def infer_language_from_filename(file_name: str | None) -> str | None:
    if not file_name or "." not in file_name:
        return None

    extension = file_name.rsplit(".", 1)[-1].lower()
    language_map = {
        "py": "python",
        "ipynb": "json",
        "js": "javascript",
        "jsx": "javascript",
        "ts": "typescript",
        "tsx": "typescript",
        "md": "markdown",
        "json": "json",
        "yaml": "yaml",
        "yml": "yaml",
        "toml": "toml",
        "ini": "ini",
        "cfg": "ini",
        "html": "html",
        "css": "css",
        "scss": "scss",
        "sh": "bash",
        "bat": "bat",
        "ps1": "powershell",
        "txt": "text",
        "csv": "csv",
    }
    return language_map.get(extension, "text")


def ask_question(question: str) -> AssistantResponse:
    try:
        result = workflow.invoke(
            {
                "messages": [
                    HumanMessage(content=question)
                ]
            }
        )
        content = result["messages"][-1].content
        if isinstance(content, list):
            text = ""
            for block in content:
                if block.get("type") == "text":
                    text += block.get("text", "")
            content = text

        requested_file = extract_requested_file_name(question)

        if requested_file and is_file_content_request(question):
            return {
                "content": content,
                "render_mode": "code",
                "language": infer_language_from_filename(requested_file),
            }

        return {
            "content": content,
            "render_mode": "markdown",
            "language": None,
        }

    except Exception as e:
        return {
            "content": f"Error: {e}",
            "render_mode": "markdown",
            "language": None,
        }


# ===== STREAMLIT UI =====

st.title("🤖 GitHub Repository Assistant")
st.markdown("Clone any GitHub repository, build a vector database from its code, and ask questions about it.")

# --- Sidebar: Repository configuration ---
with st.sidebar:
    st.header("📦 Repository Setup")
    repo_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/username/repo",
        help="Enter the full URL of the GitHub repository you want to analyze"
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        process_btn = st.button("🚀 Process Repository", use_container_width=True)
    with col2:
        clear_btn = st.button("🗑️ Clear Session", use_container_width=True)

    if clear_btn:
        for key in ["repo_processed", "messages"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.divider()
    st.markdown("### ℹ️ How it works")
    st.markdown("""
    1. **Enter** a GitHub repository URL
    2. **Click** "Process Repository" to clone and index the code
    3. **Ask** questions about the repository in natural language
    4. **Get** answers grounded in the actual codebase
    """)

# --- Main area ---
if process_btn:
    if not repo_url:
        st.error("⚠️ Please enter a GitHub repository URL")
    else:
        success = process_repository(repo_url)
        if success:
            st.session_state["repo_processed"] = True
            st.session_state["repo_url"] = repo_url

# --- Chat interface ---
if st.session_state.get("repo_processed"):
    st.success(f"✅ Repository ready! Ask anything about the code.")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message.get("render_mode") == "code":
                st.code(message["content"], language=message.get("language") or "text")
            else:
                st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about the repository..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = ask_question(prompt)
            if answer["render_mode"] == "code":
                st.code(answer["content"], language=answer["language"] or "text")
            else:
                st.markdown(answer["content"])

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer["content"],
            "render_mode": answer["render_mode"],
            "language": answer["language"],
        })

else:
    st.info("👈 Enter a GitHub repository URL in the sidebar and click **Process Repository** to get started.")

    # Show a placeholder illustration / explanation
    st.markdown("""
    ---
    ### 🚀 Ready to explore any GitHub repository

    This tool lets you:
    - **Clone** any public GitHub repository
    - **Index** its source code into a searchable vector database
    - **Answer** questions about the code using AI

    **Example questions you can ask:**
    - *"What does the main function do?"*
    - *"How is authentication handled?"*
    - *"What are the key classes and their relationships?"*
    - *"Find all API endpoint definitions"*
    """)