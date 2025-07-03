# Simple MCP ChatBot

A Python chatbot that integrates with Ollama and multiple Model Context Protocol (MCP) servers to provide AI assistance with various tools and capabilities.

---

## Features

- **Ollama Integration**: Uses local Ollama models for AI responses  
- **MCP Server Support**: Connects to multiple MCP servers for extended functionality  
- **Tool Execution**: Automatically executes tools based on AI responses  
- **Interactive Chat**: Command-line interface for conversational interaction  

---

## Supported MCP Servers

- **Filesystem**: File system operations and management  
- **Fetch**: Web content fetching capabilities  
- **PostgreSQL**: Database operations and queries  
- **Web Search**: Internet search functionality - local server example

---

## Prerequisites

- Python>=3.10
- Ollama installed and running locally  
- Node.js (required for some MCP servers)   

---

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/nirai2001/mcp_ollama.git
cd mcp-ollama
```
2.  **Install Python dependencies**
```bash
pip install -r requirements.txt
```
3. **Set up environment variables by creating a .env file**
```bash
OLLAMA_MODEL=llama3.1
```
4. **Configure your MCP servers in server_config.json**
```bash
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    },
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql:your-db-url"
      ]
    },
    "websearch": {
      "command": "uv",
      "args": ["run", "local_server/web_search.py"]
    }
  }
}
```

## Run the chatbot
```bash
python mcp_ollama_client.py
```
## Start chatting!
The bot will automatically use available tools when needed.

## License
**MIT License**
Copyright (c) 2024 [Nirai pandiyan pandiyaraj]
