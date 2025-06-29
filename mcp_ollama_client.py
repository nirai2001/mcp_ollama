from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack
import json
import asyncio
import requests
import os

load_dotenv()

class SimpleMCPChatBot:
    def __init__(self):
        self.sessions = []
        self.exit_stack = AsyncExitStack()
        self.ollama_url = "http://localhost:11434/api/chat"
        self.model_name = os.getenv('OLLAMA_MODEL', 'llama3.1')
        self.available_tools = []
        self.tool_to_session = {}

    def call_ollama(self, messages):
        """Call Ollama API with messages"""
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "tools": self.format_tools_for_ollama() if self.available_tools else None
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error calling Ollama: {e}")
            return None

    def format_tools_for_ollama(self):
        """Convert MCP tools format to Ollama tools format"""
        ollama_tools = []
        for tool in self.available_tools:
            ollama_tool = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"]
                }
            }
            ollama_tools.append(ollama_tool)
        return ollama_tools

    async def connect_to_server(self, server_name: str, server_config: dict):
        """Connect to a single MCP server"""
        try:
            server_params = StdioServerParameters(**server_config)
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = stdio_transport
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await session.initialize()
            self.sessions.append(session)
            
            # Get available tools
            response = await session.list_tools()
            tools = response.tools
            print(f"Connected to {server_name} with tools: {[t.name for t in tools]}")
            
            for tool in tools:
                self.tool_to_session[tool.name] = session
                self.available_tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                })
                
        except Exception as e:
            print(f"Failed to connect to {server_name}: {e}")

    async def connect_to_servers(self):
        """Connect to all configured MCP servers"""
        try:
            with open("server_config.json", "r") as file:
                data = json.load(file)
            
            servers = data.get("mcpServers", {})
            for server_name, server_config in servers.items():
                await self.connect_to_server(server_name, server_config)
                
        except Exception as e:
            print(f"Error loading server configuration: {e}")
            raise

    async def execute_tool(self, tool_name: str, tool_args: dict, tool_id: str):
        """Execute a tool and return the result"""
        try:
            if tool_name in self.tool_to_session:
                session = self.tool_to_session[tool_name]
                print(f" Executing {tool_name}...")
                
                result = await session.call_tool(tool_name, arguments=tool_args)
                
                print(f" {tool_name} completed")
                return {
                    "role": "tool",
                    "tool_call_id": tool_id,
                    "content": str(result.content)
                }
            else:
                print(f" Tool {tool_name} not found")
                return {
                    "role": "tool",
                    "tool_call_id": tool_id,
                    "content": f"Error: Tool {tool_name} not found"
                }
                
        except Exception as e:
            print(f" Error executing {tool_name}: {e}")
            return {
                "role": "tool", 
                "tool_call_id": tool_id,
                "content": f"Error: {str(e)}"
            }

    async def process_query(self, query):
        """Process a user query"""
        messages = [{'role': 'user', 'content': query}]
        
        while True:
            # Call Ollama
            response_data = self.call_ollama(messages)
            if not response_data:
                print("Failed to get response from Ollama")
                break
                
            response = response_data.get('message', {})
            assistant_content = response.get('content', '')
            tool_calls = response.get('tool_calls', [])
            
            if tool_calls:
                # Handle tool calls
                if assistant_content:
                    print(f"Assistant: {assistant_content}")
                messages.append({'role': 'assistant', 'content': assistant_content, 'tool_calls': tool_calls})
                
                # Execute tools
                for tool_call in tool_calls:
                    tool_name = tool_call.get('function', {}).get('name')
                    tool_args = tool_call.get('function', {}).get('arguments', {})
                    tool_id = tool_call.get('id', 'default_id')
                    
                    # Parse arguments if they're a string
                    if isinstance(tool_args, str):
                        try:
                            tool_args = json.loads(tool_args)
                        except json.JSONDecodeError:
                            print(f"Error parsing tool arguments: {tool_args}")
                            continue
                    
                    # Execute tool
                    result = await self.execute_tool(tool_name, tool_args, tool_id)
                    messages.append(result)
            else:
                # No tool calls, print response and end
                if assistant_content:
                    print(f"Assistant: {assistant_content}")
                break

    async def chat_loop(self):
        """Run interactive chat loop"""
        print(f"\nSimple MCP Chatbot with model: {self.model_name}")
        print(f"Connected to {len(self.sessions)} MCP server(s)")
        print(f"Available tools: {[tool['name'] for tool in self.available_tools]}")
        print("Type your queries or 'quit' to exit.\n")
        
        while True:
            try:
                query = input("Query: ").strip()
                
                if query.lower() == 'quit':
                    break
                
                print()
                await self.process_query(query)
                print("\n" + "="*50 + "\n")
                    
            except KeyboardInterrupt:
                print("\n\n Goodbye!")
                break
            except Exception as e:
                print(f"\n Error: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        print("Cleaning up...")
        await self.exit_stack.aclose()


async def main():
    chatbot = SimpleMCPChatBot()
    try:
        await chatbot.connect_to_servers()
        await chatbot.chat_loop()
    finally:
        await chatbot.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
