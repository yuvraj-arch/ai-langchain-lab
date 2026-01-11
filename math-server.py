from fastmcp import FastMCP

mcp = FastMCP("Math")

@mcp.tool()
def add(x: int, y: int) -> int:
    """Add two numbers"""
    return x + y

@mcp.tool()
def subtract(x: int, y: int) -> int:
    """Subtract two numbers"""
    return x - y

@mcp.tool()
def multiply(x: int, y: int) -> int:
    """Multiply two numbers"""
    return x * y

@mcp.tool()
def divide(x: int, y: int) -> int:
    """Divide two numbers"""
    return x / y

if __name__ == "__main__":
    mcp.run(transport="sse")