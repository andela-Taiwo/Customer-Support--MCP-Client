"""
Streamlit Customer Support Chatbot Application
Provides a web interface for the customer support chatbot
Automatically connects to MCP server and lists available tools
"""

import streamlit as st
import asyncio
from typing import List, Dict
from mcp_client import get_client, MCP_SERVER_URL
from utils.logger import get_logger

logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="Customer Support Chatbot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better UI
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stChatMessage {
        padding: 1rem;
    }
    .status-box {
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .status-connected {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .status-disconnected {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "client_initialized" not in st.session_state:
    st.session_state.client_initialized = False
if "client" not in st.session_state:
    st.session_state.client = None
if "tools" not in st.session_state:
    st.session_state.tools = []


def auto_initialize_client():
    """Automatically initialize the MCP client on app startup"""
    if not st.session_state.client_initialized:
        with st.spinner("🔌 Auto-connecting to MCP server and loading tools..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                # Get client with auto_connect=True to ensure initialization
                client = loop.run_until_complete(get_client(auto_connect=True))
                st.session_state.client = client

                # Ensure client is initialized
                if not client._initialized:
                    logger.info("Client not initialized, initializing now...")
                    loop.run_until_complete(client.initialize())

                # Get tools after initialization
                tools = client.get_available_tools()
                st.session_state.tools = tools if tools else []

                # Log for debugging
                if tools:
                    st.success(f"✅ Connected! Loaded {len(tools)} tools.")
                else:
                    st.warning("⚠️ Connected but no tools found.")

                st.session_state.client_initialized = True
                return True
            except Exception as e:
                st.error(f"Failed to auto-initialize client: {str(e)}")
                import traceback

                st.error(traceback.format_exc())
                return False
    return True


async def process_message(user_input: str) -> str:
    """Process user message and get response"""
    if not st.session_state.client:
        return "Error: Client not initialized. Please refresh the page."

    # Convert session state messages to format expected by agent
    conversation_history = []
    for msg in st.session_state.messages[:-1]:  # Exclude the current message
        role = "user" if msg["role"] == "user" else "assistant"
        conversation_history.append({"role": role, "content": msg["content"]})

    response = await st.session_state.client.chat(user_input, conversation_history)
    return response


def main():
    """Main application"""
    # Header
    st.markdown(
        '<div class="main-header">🖥️ Customer Support Chatbot</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sub-header">Get help with computer products: monitors, printers, and more</div>',
        unsafe_allow_html=True,
    )

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.info(f"**MCP Server:**\n{MCP_SERVER_URL}")

        # Auto-connect status
        if st.session_state.client_initialized:
            st.success("✓ Auto-connected")
            if st.button("🔄 Reconnect"):
                st.session_state.client_initialized = False
                st.session_state.client = None
                st.rerun()
        else:
            st.warning("⚠️ Not connected")
            if st.button("🔌 Connect Now", type="primary"):
                if auto_initialize_client():
                    st.success("✓ Connected successfully!")
                    st.rerun()

        st.divider()

        # Show available tools
        st.subheader("🛠️ Available Tools")
        if st.session_state.client_initialized and st.session_state.client:
            # Refresh tools from client
            try:
                # Ensure client is initialized before getting tools
                if not st.session_state.client._initialized:
                    with st.spinner("Initializing client..."):
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(st.session_state.client.initialize())

                current_tools = st.session_state.client.get_available_tools()
                if current_tools:
                    st.session_state.tools = current_tools
                    for i, tool in enumerate(st.session_state.tools, 1):
                        st.text(f"{i}. {tool}")
                    st.caption(f"Total: {len(st.session_state.tools)} tools")
                else:
                    st.info(
                        "No tools available yet. Tools will appear after connection."
                    )
            except Exception as e:
                st.warning(f"Could not retrieve tools: {str(e)}")
                if st.session_state.tools:
                    for i, tool in enumerate(st.session_state.tools, 1):
                        st.text(f"{i}. {tool}")
        elif st.session_state.tools:
            for i, tool in enumerate(st.session_state.tools, 1):
                st.text(f"{i}. {tool}")
        else:
            st.info("No tools available. Connect to server to load tools.")

        st.divider()

        # Clear conversation
        if st.button("🗑️ Clear Conversation"):
            st.session_state.messages = []
            st.rerun()

        # Instructions
        st.markdown("""
        ### 📝 Instructions
        - Ask questions about products
        - Get technical support
        - Check order status
        - Learn about specifications
        """)

    # Auto-initialize client on first load
    if not st.session_state.client_initialized:
        auto_initialize_client()

    # Status indicator
    if st.session_state.client_initialized:
        st.markdown(
            '<div class="status-box status-connected">✓ Auto-connected to MCP Server</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-box status-disconnected">⚠️ Not Connected - Click "Connect Now" in sidebar</div>',
            unsafe_allow_html=True,
        )

    # Chat interface
    if st.session_state.client_initialized:
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask me anything about our products..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get and display assistant response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        response = loop.run_until_complete(process_message(prompt))
                        st.markdown(response)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": response}
                        )
                    except Exception as e:
                        error_msg = f"Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": error_msg}
                        )
    else:
        st.info(
            "Please connect to the MCP server using the button in the sidebar to start chatting."
        )


if __name__ == "__main__":
    main()
