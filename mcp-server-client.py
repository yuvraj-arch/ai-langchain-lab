from fastmcp import FastMCP
import asyncio
import sys
import json
import os
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class Agent:
    def __init__(self, session):
        self.session = session
        self.client = OpenAI()
        self.messages = []
        self.tools = []

    async def initialize(self):
        # Load tools from MCP session and convert to OpenAI format
        tools_result = await self.session.list_tools()
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            }
            for tool in tools_result.tools
        ]

    async def chat(self, user_input: str):
        self.messages.append({"role": "user", "content": user_input})
        
        # Initial call
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.messages,
            tools=self.tools
        )

        response_message = response.choices[0].message
        
        # Check if the model wants to use tools
        if response_message.tool_calls:
            self.messages.append(response_message)
            
            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                # Execute tool
                result = await self.session.call_tool(tool_name, tool_args)
                
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result.content)
                })

            # Get final response after tool execution
            final_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.messages,
                tools=self.tools
            )
            final_content = final_response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": final_content})
            return final_content
        else:
            self.messages.append(response_message)
            return response_message.content

async def run_client():
    # Start MCP server (running this same file as a server)
    server = StdioServerParameters(
        command=sys.executable,
        args=[__file__, "server"]
    )

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            agent = Agent(session)
            await agent.initialize()

            print("Agent initialized. Asking question...")
            question = "What is 47 + 30?"
            print(f"User: {question}")
            
            answer = await agent.chat(question)
            print(f"Agent: {answer}")


if __name__ == "__main__":
    asyncio.run(run_client())
