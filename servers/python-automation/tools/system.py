import os
import platform
from mcp.server.fastmcp import FastMCP

def register(mcp: FastMCP):
    """Registers system tools to the provided FastMCP server instance."""
    
    @mcp.tool()
    def get_system_environment() -> str:
        """Returns the current server OS and hardware architecture details."""
        return f"OS: {platform.system()} | Release: {platform.release()} | Machine: {platform.machine()}"

    @mcp.tool()
    def get_cpu_count() -> int:
        """Returns the total number of logical CPUs available on the host."""
        return os.cpu_count() or 1