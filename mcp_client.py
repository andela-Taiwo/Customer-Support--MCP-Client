import asyncio
import os
from typing import List, Optional, Dict, Any
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from dotenv import load_dotenv
import requests
from utils.logger import get_logger
from config import settings

load_dotenv()

logger = get_logger(__name__)

MCP_SERVER_URL = os.getenv(
    "MCP_SERVER_URL", "https://vipfapwm3x.us-east-1.awsapprunner.com/mcp"
)

GROQ_API_KEY = settings.GROQ_API_KEY
OPENAI_API_KEY = settings.OPENAI_API_KEY
MODEL = settings.model


class CustomerSupportMCPClient:
    def __init__(self):
        self.mcp_client: Optional[MultiServerMCPClient] = None
        self.agent = None
        self.model = None
        self.tools = []
        self._initialized = False

    async def check_server_connection(self) -> bool:
        try:
            response = await asyncio.to_thread(
                requests.get, MCP_SERVER_URL, timeout=5
            )
            return response.status_code < 500
        except Exception as e:
            logger.error(f"Srver conection check failed: {e}")
            return False

    async def list_available_tools(self) -> List[str]:
        if not self.tools:
            return []

        tool_names = []
        logger.info("=" * 60)
        logger.info("Available Tools from MCP Server:")
        logger.info("=" * 60)

        for i, tool in enumerate(self.tools, 1):
            tool_name = tool.name if hasattr(tool, "name") else "Unknown"
            tool_names.append(tool_name)
            desc = (
                tool.description
                if hasattr(tool, "description") and tool.description
                else "No description"
            )
            logger.info(f"{i}. {tool_name}")
            logger.info(f"   Description: {desc[:100]}...")


        return tool_names

    async def initialize(self) -> bool:
        if self._initialized:
            return True

        try:
            logger.info(f"Auto-connecting to MCP server at {MCP_SERVER_URL}...")
            server_accessible = await self.check_server_connection()
            if not server_accessible:
                logger.warning(
                    f"MCP server may not be accessible at {MCP_SERVER_URL}"
                )
                logger.warning("Continuing anyway, but tools may not work...")
            else:
                logger.info("Server connection successful!")

            logger.info("Initializing MCP client...")
            self.mcp_client = MultiServerMCPClient(
                {
                    "customer_support": {
                        "url": MCP_SERVER_URL,
                        "transport": "streamable_http",
                    }
                }
            )

            logger.info("Retrieving tools from MCP server...")
            tools = await self.mcp_client.get_tools()
            self.tools = list(tools) if tools else []
            print(self.tools, 'TOOLS')
            logger.info(f"Retrieved {len(self.tools)} raw tools from server")

            if not self.tools:
                logger.warning("No tools retrieved from MCP server")
                return False

            logger.info(f"Retrieved {len(self.tools)} tools from server")

            valid_tools = []
            for tool in self.tools:
                if not hasattr(tool, "name"):
                    logger.warning(f"Tool missing name attribute: {tool}")
                    continue
                valid_tools.append(tool)

            self.tools = valid_tools

            if not self.tools:
                logger.error("No valid tools retrieved from MCP server!")
                return False

            await self.list_available_tools()

            if not GROQ_API_KEY and not OPENAI_API_KEY:
                raise ValueError(
                    "GROQ_API_KEY or OPENAI_API_KEY not found in environment variables"
                )

            if OPENAI_API_KEY:
                self.model = ChatOpenAI(
                    model="gpt-5-mini", temperature=0.3, api_key=OPENAI_API_KEY
                )
            elif GROQ_API_KEY:
                self.model = ChatGroq(
                    model="llama-3.1-8b-instant", temperature=0.3, api_key=GROQ_API_KEY
                )
            else:
                raise ValueError(
                    "GROQ_API_KEY or OPENAI_API_KEY not found in environment variables"
                )

            logger.info("Binding tools to model...")
            model_with_tools = self.model.bind_tools(self.tools)

            logger.info("Creating agent...")
            self.agent = create_agent(model_with_tools, tools=self.tools)

            self._initialized = True
            logger.info("Customer Support chatbot initialized successfully!")
            return True

        except Exception as e:
            logger.error(f"Error initializing MCP client: {e}", exc_info=True)
            return False

    async def chat(
        self, user_message: str, conversation_history: Optional[List] = None
    ) -> str:
        if not self._initialized:
            await self.initialize()

        if not self.agent:
            return (
                "Error: Agent not initialized. Please check the MCP server connection."
            )

        try:
            messages = []

            system_message = (
                "You are a helpful customer support assistant for a company that sells "
                "computer products like monitors, printers, and other computer accessories. "
                "You should be friendly, professional, and focused on helping customers with "
                "their questions about products, orders, technical suport, and general inquiries. "
                f"You have access to the following tools: {', '.join([tool.name for tool in self.tools])}. "
                "Use these tools to help answer customer questions accurately."
                "If the user asks a question that is not related to the tools, please say that you are not able to answer that question."
            )
            messages.append({"role": "system", "content": system_message})

            if conversation_history:
                messages.extend(conversation_history)

            messages.append({"role": "user", "content": user_message})

            config = {"recursion_limit": 50}
            result = await self.agent.ainvoke({"messages": messages}, config=config)

            if result and "messages" in result and len(result["messages"]) > 0:
                response = result["messages"][-1].content
                return (
                    response
                    if response
                    else "I apologize, but I couldn't generate a response. Please try again."
                )
            else:
                return (
                    "I apologize, but I couldn't generate a response. Please try again."
                )

        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            logger.error(f"Error processing message: {error_msg}", exc_info=True)
            return f"I encountered an error: {error_msg}. Please try again or rephrase your question."

    def get_available_tools(self) -> List[str]:
        if not self.tools:
            logger.warning("No tools available in client")
            return []

        if not self._initialized:
            logger.warning("Client not initialized, cannot get tools")
            return []

        tool_names = []
        for tool in self.tools:
            if hasattr(tool, "name") and tool.name:
                tool_names.append(tool.name)
            elif hasattr(tool, "__name__"):
                tool_names.append(tool.__name__)
            else:
                tool_str = str(tool)
                if "name=" in tool_str:
                    try:
                        name = tool_str.split("name=")[1].split(",")[0].strip("'\"")
                        tool_names.append(name)
                    except:
                        pass

        return tool_names


client_instance_obj = None


async def get_client(auto_connect: bool = True) -> CustomerSupportMCPClient:
    global client_instance_obj
    if client_instance_obj is None:
        client_instance_obj = CustomerSupportMCPClient()
        if auto_connect:
            await client_instance_obj.initialize()
    elif auto_connect and not client_instance_obj._initialized:
        await client_instance_obj.initialize()
    return client_instance_obj
