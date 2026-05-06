#!/usr/bin/env python
# cursor_compatible.py - Works with uv
import subprocess
import sys
import os

def run_with_uv():
    """Re-run this script with uv if psutil is missing"""
    try:
        import psutil
        return False  # psutil exists, continue normally
    except ImportError:
        print("🔄 Running with uv to handle dependencies...")
        # Re-run the same script with uv
        cmd = [
            "uv", "run",
            "--with", "psutil",
            "--with", "mcp[cli]",
            "python",
            __file__
        ] + sys.argv[1:]
        subprocess.run(cmd)
        return True  # Handled by uv

if __name__ == "__main__":
    if run_with_uv():
        sys.exit(0)
    
    # Original code continues here
    import psutil
    import platform
    import os as os_module
    
    SAFE_DIRECTORY = os_module.path.abspath("C:/repositories/lizardinteractive-mcp-core")
    
    def get_system_report():
        cpu_usage = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return f"""--- Lizard System Report ---
OS: {platform.system()} {platform.release()}
CPU Load: {cpu_usage}%
RAM: {ram.percent}% used ({ram.available // (1024**2)}MB available of {ram.total // (1024**2)}MB)
Disk: {disk.percent}% used ({disk.free // (1024**3)}GB free)"""
    
    def create_automation_note(filename: str, content: str):
        target_path = os_module.path.join(SAFE_DIRECTORY, filename)
        abs_path = os_module.path.abspath(target_path)
        if os_module.path.commonpath([abs_path, SAFE_DIRECTORY]) != SAFE_DIRECTORY:
            return "Error: Path outside of safe directory."
        
        os_module.makedirs(os_module.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w") as f:
            f.write(content)
        return f"Success: Note saved to {filename}"
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "report":
            print(get_system_report())
        elif sys.argv[1] == "note" and len(sys.argv) > 2:
            print(create_automation_note(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else ""))
    else:
        print(get_system_report())