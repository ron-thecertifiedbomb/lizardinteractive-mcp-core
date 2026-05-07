import os
import subprocess
import sys
import shutil
from mcp.server.fastmcp import FastMCP
from config import SAFE_DIRECTORY
from utils.security import is_safe_path


def register(mcp: FastMCP):

    @mcp.tool()
    def seed_to_mongo(script_path: str = "scripts/seed-blog.ts") -> str:
        """Triggers the existing Node.js script to seed the database."""
        full_path = os.path.join(SAFE_DIRECTORY, script_path)
        if not is_safe_path(full_path):
            return "Security Error: Script location is outside safe repository."

        try:
            # Use shutil.which to find the true path to npx, avoiding shell=True.
            # This is more secure and reliable, especially on Windows where npx is a .cmd file.
            npx_path = shutil.which("npx")
            if not npx_path:
                return "System Error: 'npx' command not found. Is Node.js installed and in your PATH?"

            result = subprocess.run(
                [npx_path, "tsx", full_path],
                capture_output=True,
                text=True,
                check=True,
                shell=False
            )
            return f"--- Database Seed Report ---\n{result.stdout}"
        except subprocess.CalledProcessError as e:
            return f"Error during seeding: {e.stderr}"
        except Exception as e:
            return f"System Error: {str(e)}"