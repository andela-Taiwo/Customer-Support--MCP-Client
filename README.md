# Customer Support Chatbot

A production-ready Customer Support chatbot for a company selling computer products (monitors, printers, etc.) that integrates with the company's MCP (Model Context Protocol) server using Streamable HTTP transport.

## 🎯 Overview

This application provides an AI-powered customer support interface that:
- Connects to an MCP server to access company tools and resources
- Uses OpenAI GPT-4o-mini or Groq LLM for natural language understanding
- Provides a user-friendly Streamlit web interface
- Automatically discovers and lists available tools from the MCP server
- Handles customer inquiries about products, orders, and technical support

## ✨ Features

- 🤖 **AI-Powered Chatbot**: Uses OpenAI GPT-4o-mini or Groq LLM for intelligent responses
- 🔌 **MCP Server Integration**: Connects to company MCP server via Streamable HTTP
- 💬 **Interactive Web Interface**: Beautiful Streamlit-based chat interface
- 🛠️ **Automatic Tool Discovery**: Automatically discovers and lists available tools
- 📝 **Conversation History**: Maintains context across conversation turns
- 📊 **Logging**: Comprehensive logging system for debugging and monitoring
- ⚡ **Auto-Connect**: Automatically connects to MCP server on startup
- 🔄 **Error Handling**: Robust error handling with user-friendly messages

## 📋 Prerequisites

- Python 3.13 or higher
- OpenAI API key (for GPT-4o-mini) or Groq API key (for Groq models)
- Access to the MCP server at `https://vipfapwm3x.us-east-1.awsapprunner.com/mcp`

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/andela-Taiwo/Customer-Support--MCP-Client.git
cd Customer-Support--MCP-Client
```

### 2. Install Dependencies

**Option A: Using pip**
```bash
pip install -r requirements.txt
```

**Option B: Using uv (recommended)**
```bash
uv sync
```

**Option C: Using setup.py**
```bash
pip install -e .
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```env
# MCP Server Configuration
MCP_SERVER_URL=https://vipfapwm3x.us-east-1.awsapprunner.com/mcp

# LLM API Keys (use one or both)
OPENAI_API_KEY=your_openai_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

## 🔧 Configuration

The application uses `config.py` for default settings:

- **MCP_SERVER_URL**: Default MCP server endpoint
- **Model**: Default LLM model (configurable in code)
- **Temperature**: Set to 0.3 for consistent responses

You can override these settings via environment variables in your `.env` file.

## 📱 Usage

### Running the Application

**Option 1: Direct Streamlit command**
```bash
streamlit run chatbot_app.py
```

**Option 2: Using Python**
```bash
python -m streamlit run chatbot_app.py
```

The application will open in your default web browser at `http://localhost:8501`.

### Using the Chatbot

1. **Auto-Connection**: The app automatically connects to the MCP server on startup
2. **View Tools**: Check the sidebar to see all available tools from the MCP server
3. **Start Chatting**: Type your questions in the chat input at the bottom
4. **View History**: All conversation history is maintained during the session
5. **Clear Chat**: Use the "Clear Conversation" button to reset the chat

### Example Questions

- "What monitors do you have in stock?"
- "I need help setting up my printer"
- "What are the specifications of your 4K monitors?"
- "I have an issue with my recent order"
- "Can you recommend a monitor for graphic design?"
- "Show me all available printers"

## 🔄 Application Workflow

### 1. Application Startup

```
┌─────────────────────────────────────┐
│   Streamlit App Starts              │
│   (chatbot_app.py)                  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Initialize Session State          │
│   - messages = []                  │
│   - client_initialized = False     │
│   - client = None                  │
│   - tools = []                     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Call auto_initialize_client()    │
└──────────────┬──────────────────────┘
               │
               ▼
```

### 2. Client Initialization

```
┌─────────────────────────────────────┐
│   Get MCP Client                    │
│   get_client(auto_connect=True)     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Create CustomerSupportMCPClient    │
│   - mcp_client = None              │
│   - agent = None                   │
│   - model = None                   │
│   - tools = []                     │
│   - _initialized = False           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Call initialize()                │
└──────────────┬──────────────────────┘
               │
               ▼
```

### 3. MCP Server Connection

```
┌─────────────────────────────────────┐
│   Check Server Connection           │
│   check_server_connection()         │
└──────────────┬──────────────────────┘
               │
               ├─── Success ────► Continue
               │
               └─── Failure ────► Log Warning, Continue Anyway
               │
               ▼
┌─────────────────────────────────────┐
│   Initialize MultiServerMCPClient   │
│   - URL: MCP_SERVER_URL             │
│   - Transport: streamable_http    │
└──────────────┬──────────────────────┘
               │
               ▼
```

### 4. Tool Discovery

```
┌─────────────────────────────────────┐
│   Retrieve Tools from MCP Server    │
│   mcp_client.get_tools()            │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Validate Tools                    │
│   - Check for name attribute        │
│   - Filter invalid tools            │
│   - Store in self.tools             │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   List Available Tools              │
│   list_available_tools()            │
│   - Log tool names & descriptions   │
│   - Display in console/logs         │
└──────────────┬──────────────────────┘
               │
               ▼
```

### 5. LLM Model Initialization

```
┌─────────────────────────────────────┐
│   Initialize LLM Model              │
│   - ChatOpenAI (GPT-4o-mini)        │
│     OR                              │
│   - ChatGroq (Llama models)         │
│   - Temperature: 0.3                │
│   - API Key from environment        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Bind Tools to Model               │
│   model.bind_tools(tools)           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Create LangGraph Agent            │
│   create_react_agent(model, tools)  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Mark as Initialized               │
│   _initialized = True               │
└──────────────┬──────────────────────┘
               │
               ▼
```

### 6. User Interaction Flow

```
┌─────────────────────────────────────┐
│   User Types Message                │
│   (Streamlit chat input)            │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Add to Session State              │
│   messages.append(user_message)      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Process Message                   │
│   process_message(user_input)        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Prepare Conversation History      │
│   - Convert session messages        │
│   - Format for agent                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Call client.chat()                │
└──────────────┬──────────────────────┘
               │
               ▼
```

### 7. Agent Processing

```
┌─────────────────────────────────────┐
│   Build Message Context             │
│   - System message (role & context) │
│   - Conversation history            │
│   - Current user message            │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Invoke LangGraph Agent           │
│   agent.ainvoke(messages)          │
└──────────────┬──────────────────────┘
               │
               ├─── Agent Decides ────►
               │    - Use tool?        │
               │    - Respond directly?│
               │
               ▼
┌─────────────────────────────────────┐
│   Tool Execution (if needed)       │
│   - Agent calls MCP tool            │
│   - Tool executes on MCP server      │
│   - Results returned to agent       │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Generate Response                 │
│   - Agent formulates answer          │
│   - Uses tool results if available  │
│   - Returns final response           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Display Response                  │
│   - Add to session state            │
│   - Show in Streamlit chat UI        │
└─────────────────────────────────────┘
```

### 8. Tool Execution Flow

```
┌─────────────────────────────────────┐
│   Agent Identifies Tool Need        │
│   (e.g., list_products, get_order) │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Agent Calls Tool                  │
│   - Tool name                        │
│   - Tool arguments                   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   MCP Client Routes Request         │
│   - Via streamable_http transport   │
│   - To MCP server endpoint          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   MCP Server Executes Tool          │
│   - Processes request                │
│   - Returns results                  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Results Returned to Agent          │
│   - Agent processes results          │
│   - Incorporates into response       │
└─────────────────────────────────────┘
```

## 🏗️ Architecture

### Project Structure

```
MCP-assessment/
├── chatbot_app.py          # Streamlit web application
├── mcp_client.py          # MCP client and agent logic
├── config.py              # Configuration settings
├── extract_tools.py       # Tool extraction utility
├── setup.py              # Package setup
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Project configuration
├── Dockerfile            # Docker configuration
├── deployment.yaml       # Deployment configuration
├── utils/
│   ├── logger.py         # Logging utility
│   └── custom_exception.py  # Custom exceptions
└── logs/                 # Application logs
```

### Component Overview

#### 1. **chatbot_app.py** - Streamlit Interface
- Web UI for user interactions
- Session state management
- Auto-initialization of MCP client
- Real-time chat interface
- Tool display in sidebar

#### 2. **mcp_client.py** - MCP Client & Agent
- `CustomerSupportMCPClient`: Main client class
  - Server connection management
  - Tool discovery and validation
  - LLM model initialization
  - Agent creation and management
  - Message processing

#### 3. **config.py** - Configuration
- Environment variable loading
- Default settings
- Model configuration

#### 4. **utils/logger.py** - Logging
- File-based logging
- Daily log rotation
- Structured log format

### Data Flow

```
User Input
    │
    ▼
Streamlit UI (chatbot_app.py)
    │
    ▼
MCP Client (mcp_client.py)
    │
    ├──► MCP Server (via HTTP)
    │    └──► Tool Execution
    │
    └──► LangGraph Agent
         │
         ├──► LLM (OpenAI/Groq)
         │
         └──► Tool Selection & Execution
              │
              └──► Response Generation
                   │
                   ▼
              User Response
```

## 🔍 Available Tools

The chatbot automatically discovers tools from the MCP server. Common tools include:

- `list_products`: List products with optional filters
- `get_product`: Get detailed product information by SKU
- `search_products`: Search products by name or description
- `get_customer`: Get customer information by ID
- `verify_customer_pin`: Verify customer identity
- `list_orders`: List orders with optional filters
- `get_order`: Get detailed order information
- `create_order`: Create a new order with items

## 📝 Logging

The application logs all operations to `logs/log_YYYY-MM-DD.log`:

- Connection attempts
- Tool discovery
- Agent initialization
- User interactions
- Errors and warnings

## 🐛 Troubleshooting

### Connection Issues

**Problem**: Cannot connect to MCP server
- **Solution**: Check your internet connection and verify the MCP server URL
- **Check**: Look at logs in `logs/` directory for detailed error messages

### No Tools Available

**Problem**: Tools list is empty
- **Solution**: Ensure MCP server is accessible and returning tools
- **Check**: Run `extract_tools.py` to test tool discovery

### API Key Issues

**Problem**: LLM not responding
- **Solution**: Verify your API keys in `.env` file
- **Check**: Ensure `OPENAI_API_KEY` or `GROQ_API_KEY` is set correctly

### Initialization Errors

**Problem**: Client fails to initialize
- **Solution**: Check logs for specific error messages
- **Check**: Verify all dependencies are installed correctly

## 🚀 Deployment

### Docker Deployment

```bash
docker build -t customer-support-chatbot .
docker run -p 8501:8501 --env-file .env customer-support-chatbot
```

### Environment Variables for Production

```env
MCP_SERVER_URL=https://vipfapwm3x.us-east-1.awsapprunner.com/mcp
OPENAI_API_KEY=your_production_key
GROQ_API_KEY=your_production_key
```

## 📄 License

This project is part of an assessment/prototype.

## 👤 Author

**Taiwo Sokunbi**
- Email: sokunbitaiwo82@gmail.com
- GitHub: [andela-Taiwo](https://github.com/andela-Taiwo)

## 🤝 Contributing

This is a prototype project. For questions or issues, please contact the author.

## 📚 Additional Resources

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [MCP Protocol](https://modelcontextprotocol.io/)

---

**Note**: This application requires active internet connection to communicate with the MCP server and LLM APIs.
