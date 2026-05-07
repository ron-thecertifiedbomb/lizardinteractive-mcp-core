from mcp.server.fastmcp import FastMCP
# Added audit to the imports to match your registrations
from tools import system,  blog, database, performance, lighthouse

mcp = FastMCP("lizard-automation")

# Call registration handlers in each module
system.register(mcp)
blog.register(mcp)
database.register(mcp)
performance.register(mcp)
lighthouse.register(mcp)

if __name__ == "__main__":
    mcp.run()