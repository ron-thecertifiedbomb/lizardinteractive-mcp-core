# 💻 Terminal & Bash Cheat Sheet

Welcome to your personal command-line cheatcode list! This document saves the complex terminal commands used to manage the Lizard MCP Core repository, broken down so you understand exactly how they work.

---

## 1. Print a Clean Directory Tree

**The Cheatcode:**
```bash
find . -type d \( -name node_modules -o -name .git -o -name __pycache__ -o -name .venv \) -prune -o -print | sed -e 's;[^/]*/;|____;g;s;____|; |;g'
```

**What it does:** 
It prints a beautiful visual tree of your project's files and folders, but explicitly ignores the massive folders (like `node_modules` and `.git`) so it doesn't flood your screen.

**How it works (Line-by-Line Breakdown):**
*   `find .`  
    Start searching right here in the current directory (`.`).
*   `-type d \( -name node_modules -o -name .git -o -name __pycache__ -o -name .venv \) -prune`  
    This first part looks for **d**irectories (`-type d`) with specific names (using `-o` for **OR**). When it finds one, `-prune` tells the system: "STOP. Do not look inside it. Prune it from the search."
*   `-o -print`  
    The `-o` means **OR**. It tells the system: "If the item wasn't pruned in the previous step, print it." Because `-type d` was only applied to the prune condition, this safely prints all remaining files **and** folders!
*   `| sed -e 's;[^/]*/;|____;g;s;____|; |;g'`  
    The `|` (pipe) sends the printed list into `sed` (a text editor tool). `sed` uses a regex replace command to swap out the boring folder paths (like `./servers/python-automation/tools`) into those cool visual tree branches (`|____`).

---

## 2. Run a Python Script

**The Cheatcode (using `uv` - Recommended):**
```bash
uv run <script_name.py>
```

**What it does:** 
It runs your Python script safely inside your project's managed environment. This ensures all your required dependencies (like `fastmcp` or `psutil`) are loaded correctly without messing up your global computer settings.

**How it works (Line-by-Line Breakdown):**
*   `uv`  
    Calls the ultra-fast Python package manager you are using for the project.
*   `run`  
    Tells `uv` to execute a command or script.
*   `<script_name.py>`  
    The actual Python file you want to execute (for example, `test_mcp_client.py`).

**Alternative (Standard Python):**
If you just want to run a simple script using your default system Python, you can use:
```bash
python <script_name.py>
```

---

## 3. Manage Python Dependencies

**The Cheatcode (Add a new package):**
```bash
uv pip install <package_name>
```

**What it does:** 
Downloads and installs a new Python package (like `requests` or `numpy`) into your project's virtual environment. `uv` will automatically update your `pyproject.toml` and `requirements.lock` files.

**The Cheatcode (Sync environment):**
```bash
uv pip sync
```
**What it does:** Reads your `pyproject.toml` or `requirements.txt` file and ensures your environment has the exact packages listed. It will install any missing ones and remove any that don't belong. This is great for setting up the project on a new machine.
