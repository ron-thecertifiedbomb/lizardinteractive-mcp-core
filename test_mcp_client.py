# test_mcp_client.py
import subprocess
import json
import sys

def send_mcp_request(tool_name, arguments=None):
    """Send a request to your MCP server"""
    
    # The request format MCP servers expect
    request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments or {}
        },
        "id": 1
    }
    
    # Start the server and send the request
    cmd = [
        "C:/Users/ronan/.local/bin/uv.exe", "run",
        "--with", "mcp[cli]",
        "--with", "psutil",
        "C:/repositories/lizardinteractive-mcp-core/servers/python-automation/server.py"
    ]
    
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send request and get response
    stdout, stderr = process.communicate(json.dumps(request))
    
    if stderr:
        print(f"Error: {stderr}", file=sys.stderr)
    
    # Parse response
    try:
        response = json.loads(stdout)
        if "result" in response:
            content = response["result"].get("content", [])
            for item in content:
                if item.get("type") == "text":
                    print(item.get("text"))
        elif "error" in response:
            print(f"Error: {response['error']}")
    except json.JSONDecodeError:
        print(stdout)

if __name__ == "__main__":
    # Test your tools
    print("Getting system report...")
    send_mcp_request("get_system_report")
    
    print("\nCreating a note...")
    send_mcp_request("create_automation_note", {
        "filename": "test_from_cursor.txt",
        "content": "This was created via MCP!"
    })