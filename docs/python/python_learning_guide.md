# 🐍 Python Learning Guide: Lizard MCP Core

Welcome to your personal Python study guide! This document breaks down the Python scripts in your repository (`server.py`, `test_mcp_client.py`, `tools/*.py`, and `cursor_compatible.py`) to help you understand the core programming concepts powering your automation server.

---

## 1. Decorators and Type Hinting (`tools/audit.py`)

In modern Python, you will frequently see the `@` symbol above functions, as well as `str` or `int` explicitly written in the function definitions.

### Type Hinting
```python
def save_code_review(target_filename: str, review_content: str) -> str:
```
*   **What it does:** The `: str` tells us the expected input type, and `-> str` tells us the function will return a string.
*   **Why it's useful:** Python doesn't *force* you to use these, but adding them helps your IDE (like Cursor or VS Code) catch bugs before you even run the code. It also helps AI know exactly what data format to send to your tools.

### Decorators
```python
@mcp.tool()
def read_pdf_audit(filename: str) -> str:
```
*   **What it does:** The `@mcp.tool()` is a **decorator**. It "wraps" your function and modifies its behavior without changing the code inside it.
*   **Why it's useful:** Under the hood, this specific decorator tells the `FastMCP` server, "Hey, register this function as an official tool that the AI can use!"

---

## 2. Managing the File System Safely (`tools/audit.py`)

When writing Python scripts that create or read files, you need to navigate the operating system reliably across Windows, Mac, and Linux. The `os` module handles this.

### Joining Paths
```python
target_path = os.path.join(AUDIT_DIRECTORY, filename)
```
*   **Why we use it:** Instead of manually typing `folder + "\\" + filename` (which breaks on Mac/Linux), `os.path.join` automatically uses the correct slash for the user's operating system.

### Security Checks (Path Traversal Prevention)
```python
abs_target = os.path.abspath(target_path)
if os.path.commonpath([abs_target, AUDIT_DIRECTORY]) != AUDIT_DIRECTORY:
    return "Security Error: Access denied."
```
*   **What it does:** This prevents a hacker or a confused AI from requesting a file like `../../../Windows/System32/secret.txt`. 
*   **How it works:** It forces the path to be absolute, and checks if the resulting file path still shares a common root with your allowed `AUDIT_DIRECTORY`.

---

## 3. Subprocessing: Making Python Control Other Programs (`test_mcp_client.py` & `tools/lighthouse.py`)

Python is a great "glue" language. The `subprocess` module allows Python to open the terminal, run commands, and read the output—just like a human would.

### `subprocess.run()` (Wait for it to finish)
```python
result = subprocess.run(
    ["node", audit_js, url, url_dir, filename],
    capture_output=True,
    text=True,
    timeout=180,
    shell=True
)
```
*   **What it does:** This tells Python to execute a Node.js script. 
*   **`capture_output=True, text=True`:** This captures the `console.log()` output from Node.js as a clean Python string so you can parse it later.
*   **`timeout=180`:** If the Lighthouse audit gets stuck, Python will forcibly kill it after 3 minutes instead of freezing forever.

### `subprocess.Popen()` (Talk to it while it runs)
```python
process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
process.stdin.write(json.dumps(tool_request) + "\n")
```
*   **What it does:** Unlike `run()`, `Popen` starts a program in the background and lets Python keep running. 
*   **`stdin=subprocess.PIPE`:** This creates a communication pipe. Python can stream real-time data into the program using `process.stdin.write()`. This is exactly how your test script talks to your MCP server!

---

## 4. Regular Expressions (Regex) (`tools/lighthouse.py`)

Regular Expressions (`re`) are a powerful mini-language for pattern matching and text manipulation.

### Slugifying Text
```python
def _slugify(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", text).strip("_")
```
*   **What it does:** It turns a messy URL like `https://www.google.com/search` into a clean filename like `www_google_com_search`.
*   **How it works:** `re.sub` stands for substitute. The pattern `[^a-zA-Z0-9_\-]` says: "Find any character that is **NOT** (`^`) a letter, number, underscore, or dash, and replace it with an underscore (`_`)."

---

## 5. Bootstrapping / Auto-Installing Dependencies (`cursor_compatible.py`)

Your `cursor_compatible.py` script has a brilliant trick: it checks if the required modules are installed, and if not, it uses `uv` to automatically install them and re-run itself.

```python
def run_with_uv():
    try:
        import psutil
        return False  # Success! Module exists.
    except ImportError:
        print("🔄 Running with uv to handle dependencies...")
        cmd = ["uv", "run", "--with", "psutil", "python", __file__]
        subprocess.run(cmd)
        return True  # Handled by uv
```
*   **The `try/except` block:** Python attempts to import `psutil`. If it fails, it throws an `ImportError`.
*   **The Catch:** Instead of crashing, the `except` block catches the error, builds a new terminal command to run `uv`, and restarts the current file (`__file__`) with the proper dependencies loaded.

---

## 6. Advanced String Formatting (f-strings)

You make heavy use of f-strings (`f"..."`) to generate markdown reports dynamically.

```python
summary = f"""Lighthouse Audit Complete
URL     : {url}
Folder  : {url_dir}
"""
```
*   **What it does:** By putting an `f` before the string quotes, you can directly inject Python variables into the text using curly braces `{}`. 
*   **Triple Quotes `\"\"\"`:** These allow your string to span multiple lines without having to type `\n` at the end of every sentence, which is perfect for building markdown reports and console summaries.

### Advanced f-string formatting
```python
f"Performance    : {_pct(scores.get('performance')):<6}"
```
*   **The `:<6` trick:** This formats the output to be exactly 6 characters wide, aligned to the left. If the percentage is only "95%", it adds extra spaces to ensure everything lines up perfectly like a table in the terminal!

---

## Summary
By reviewing these scripts, you've implemented advanced Python concepts:
1. **Inter-Process Communication (IPC):** Streaming JSON data between scripts via `stdin` and `stdout`.
2. **System Administration:** Traversing and securing file paths dynamically.
3. **Data Serialization:** Converting native Python dictionaries to `JSON` and back.
4. **Automation:** Wrapping external Node.js/Command Line tools into clean Python wrappers.

Keep building!
