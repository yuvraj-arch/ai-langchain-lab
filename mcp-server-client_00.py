from dotenv import load_dotenv
import os
import sys
import json
import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from openai import OpenAI

load_dotenv()

client = OpenAI()  # uses OPENAI_API_KEY from env

async def main():
    server = StdioServerParameters(
        command=sys.executable,
        args=["math-server.py"]
    )
    # Connect to MCP server via stdio
    async with stdio_client(server) as (read, write):

        async with ClientSession(read, write) as session:
            # Load tools from server
            await session.initialize()
            
            # List tools and convert to OpenAI format
            tools_result = await session.list_tools()
            print(f"Tools: {tools_result.tools}")
            openai_tools = [
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

            user_question = "What is 47 + 30?"
            messages = [{"role": "user", "content": user_question}]

            # Ask OpenAI model
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=openai_tools
            )

            # If model wants to call a tool
            tool_calls = response.choices[0].message.tool_calls
            if tool_calls:
                # Add assistant message with tool calls to history
                messages.append(response.choices[0].message)

                for tool_call in tool_calls:
                    tool_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)

                    # Call MCP tool
                    result = await session.call_tool(tool_name, args)

                    print(f"Tool result: {result}")

                    # Add tool result to history
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result.content)
                    })

                # Get final response
                final_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=openai_tools
                )

                print(final_response.choices[0].message.content)
            else:
                print(response.choices[0].message.content)

asyncio.run(main())