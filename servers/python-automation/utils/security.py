import os
import platform
import psutil
from mcp.server.fastmcp import FastMCP
from config import SAFE_DIRECTORY


def is_safe_path(target_path: str) -> bool:
    """
    Validates that a target file path resolves strictly within the allowed safe directory.
    """
    abs_base = os.path.abspath(SAFE_DIRECTORY)
    abs_target = os.path.abspath(target_path)
    return os.path.commonpath([abs_base, abs_target]) == abs_base


def register(mcp: FastMCP):

    @mcp.tool()
    def get_system_report() -> str:
        """Returns a high-performance report of CPU, RAM, and Disk usage."""
        cpu_usage = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        return (
            f"--- Lizard System Report ---\n"
            f"OS: {platform.system()} {platform.release()}\n"
            f"CPU Load: {cpu_usage}%\n"
            f"RAM: {ram.percent}% used ({ram.available // (1024**2)}MB available of {ram.total // (1024**2)}MB)\n"
            f"Disk: {disk.percent}% used ({disk.free // (1024**3)}GB free)"
        )