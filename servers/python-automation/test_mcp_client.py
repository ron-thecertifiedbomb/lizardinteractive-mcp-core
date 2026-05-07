# test_mcp_client.py
import subprocess
import json
import os

def run_mcp_session(tool_calls):
    """Starts a single MCP server session and runs a sequence of tool calls."""
    
    # --- 1. Start the Server Process (Modular & Scalable Approach) ---
    # Dependencies are managed in requirements.txt for consistency.
    server_dir = os.path.abspath("C:/repositories/lizardinteractive-mcp-core/servers/python-automation")
    requirements_path = os.path.join(server_dir, "requirements.txt")
    server_path = os.path.join(server_dir, "server.py")

    with open(requirements_path, 'r') as f:
        dependencies = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    cmd = [
        "C:/Users/ronan/.local/bin/uv.exe", "run"
    ]
    for dep in dependencies:
        cmd.extend(["--with", dep])
    cmd.append(server_path)

    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1, # Line-buffered
        universal_newlines=True
    )

    # --- 2. Perform Handshake ---
    init_request = {"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05"}, "id": 1}
    initialized_notification = {"jsonrpc": "2.0", "method": "notifications/initialized"}

    process.stdin.write(json.dumps(init_request) + "\n")
    process.stdin.flush()
    process.stdin.write(json.dumps(initialized_notification) + "\n")
    process.stdin.flush()

    # --- 3. Execute Tool Calls Sequentially ---
    request_id_counter = 2
    for call in tool_calls:
        tool_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": call["name"],
                "arguments": call.get("args", {})
            },
            "id": request_id_counter
        }
        print(f"\n--- Calling tool: {call['name']} (ID: {request_id_counter}) ---")
        process.stdin.write(json.dumps(tool_request) + "\n")
        process.stdin.flush()
        
        # Wait for the response to this specific call before moving to the next
        while True:
            line = process.stdout.readline()
            if not line:
                break
            try:
                response = json.loads(line)
                if response.get("id") == request_id_counter:
                    if "result" in response:
                        print("--- Server Response ---")
                        content = response["result"].get("content", [])
                        for item in content:
                            if item.get("type") == "text":
                                print(item.get("text"))
                    elif "error" in response:
                         print(f"Error from server: {response['error']}")
                    break  # Move to the next tool call
            except json.JSONDecodeError:
                # Non-JSON output from server (e.g. node.js console logs)
                print(line.strip())
                
        request_id_counter += 1

    # --- 4. Cleanly shut down stdin and collect all output ---
    process.stdin.close()

    for line in iter(process.stdout.readline, ''):
        try:
            response = json.loads(line)
            # We only care about responses to our tool calls
            if "result" in response and response.get("id", 0) > 1:
                print("--- Server Response ---")
                content = response["result"].get("content", [])
                for item in content:
                    if item.get("type") == "text":
                        print(item.get("text"))
            elif "error" in response:
                 print(f"Error from server: {response['error']}")
        except json.JSONDecodeError:
            # Non-JSON output from server (e.g. console.log from node script)
            print(line.strip())
            
    # Check for any errors that occurred during the process
    stderr_output = process.stderr.read()
    if stderr_output:
        print(f"\n--- Stderr --- \n{stderr_output}")

    process.stdout.close()
    process.wait()

if __name__ == "__main__":
    # Define the sequence of tool calls we want to test.
    # This simulates what the AI does when you give it a prompt.
    audit_filename = "github_audit.pdf"
    
    test_sequence = [
        {
            "name": "run_lighthouse_audit",
            "args": {
                "url": "https://rondev.com.ph",
                "filename": audit_filename
            }
        },
        {
            "name": "read_pdf_audit",
            "args": {
                "filename": audit_filename
            }
        }
    ]
    
    run_mcp_session(test_sequence)