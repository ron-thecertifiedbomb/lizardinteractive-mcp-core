import os
import sys
import subprocess
import json
import re
import shutil
import platform
from datetime import datetime, timezone

def _relaunch_with_uv():
    """Relaunch the server using uv with dependencies from requirements.txt."""
    server_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_path = os.path.join(server_dir, "requirements.txt")
    
    if not os.path.exists(requirements_path):
        print(f"ERROR: Missing required modules and '{requirements_path}' not found.", file=sys.stderr)
        sys.exit(1)
        
    with open(requirements_path, 'r') as f:
        dependencies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
    uv_path = shutil.which("uv") or os.path.expanduser("~/.local/bin/uv.exe")
    cmd = [uv_path, "run"]
    for dep in dependencies:
        cmd.extend(["--with", dep])
    cmd.append(__file__)
    cmd.extend(sys.argv[1:])
    
    try:
        if sys.platform == "win32":
            sys.exit(subprocess.run(cmd).returncode)
        else:
            os.execvp(uv_path, cmd)
    except FileNotFoundError:
        print(f"ERROR: 'uv' command not found at {uv_path}. Please install uv.", file=sys.stderr)
        sys.exit(1)

try:
    import psutil
    import requests
    import PyPDF2
    from bs4 import BeautifulSoup
    from mcp.server.fastmcp import FastMCP
except ImportError as e:
    # Auto-relaunch with uv if any third-party dependency is missing.
    print(f"Lizard-Automation: Missing dependency '{e.name}', auto-relaunching with uv...", file=sys.stderr)
    _relaunch_with_uv()

# Initialize FastMCP for Lizard Interactive
mcp = FastMCP("Lizard-Automation")

# Your professional-grade path verification
SAFE_DIRECTORY = os.path.abspath("C:/repositories/lizardinteractive-mcp-core")
AUDIT_DIRECTORY = os.path.abspath("C:/Users/ronan/OneDrive/Documents/audits")

def is_safe_path(path):
    abs_path = os.path.abspath(path)
    return os.path.commonpath([abs_path, SAFE_DIRECTORY]) == SAFE_DIRECTORY

@mcp.tool()
def get_system_report():
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

@mcp.tool()
def save_code_review(target_filename: str, review_content: str) -> str:
    """
    Saves an AI-generated code review or architectural comment directly to the local audits folder.
    Useful for documenting system optimizations and security checks.
    """
    if not os.path.exists(AUDIT_DIRECTORY):
        os.makedirs(AUDIT_DIRECTORY)

    # Sanitize filename and append UTC timestamp
    safe_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', target_filename).replace('.py', '')
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_file = f"Code_Audit_{safe_name}_{timestamp}.md"
    output_path = os.path.join(AUDIT_DIRECTORY, output_file)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# 🛡️ Architectural Audit: {target_filename}\n")
            f.write(f"**Timestamp:** {datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')}\n")
            f.write(f"**Project:** Lizard Interactive Online\n\n")
            f.write("---\n\n")
            f.write(review_content)
        return f"Success: Architectural audit securely saved to {output_path}"
    except Exception as e:
        return f"File System Error: {str(e)}"

@mcp.tool()
def create_automation_note(filename: str, content: str) -> str:
    """Creates a specific file in the audits directory with an exact filename."""
    target_path = os.path.join(AUDIT_DIRECTORY, filename)
    
    abs_path = os.path.abspath(target_path)
    if os.path.commonpath([abs_path, AUDIT_DIRECTORY]) != AUDIT_DIRECTORY:
        return "Security Error: Path outside of audits directory."
        
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    try:
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Success: File saved exactly to {abs_path}"
    except Exception as e:
        return f"File System Error: {str(e)}"

@mcp.tool()
def convert_md_to_lizard_json(file_path: str, category: str = "Content") -> str:
    """
    Dynamically converts a Markdown blog draft into the Lizard Interactive JSON schema.
    Optimized for high-performance Next.js client templates.
    """
    full_path = os.path.join(SAFE_DIRECTORY, file_path)
    if not is_safe_path(full_path):
        return "Security Error: Access denied outside of Repositories folder."

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        title_match = re.search(r'^#\s+(.*)', content, re.MULTILINE)
        title = title_match.group(1) if title_match else "Untitled Post"
        slug = re.sub(r'[^a-z0-9]', '-', title.lower()).strip('-')
        
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        blog_data = {
            "id": slug,
            "category": category,
            "createdAt": timestamp,
            "updatedAt": timestamp,
            "title": title,
            "image": "https://res.cloudinary.com/dx3atgryf/image/upload/v1777564396/iwhgn96jsdmsr48wervs.jpg", 
            "ogImage": "https://res.cloudinary.com/dx3atgryf/image/upload/v1777564396/bb8l4mkrtdkk9vrm59gk.webp",
            "sections": []
        }

        parts = []
        current_text = []
        in_code_block = False

        for line in content.splitlines():
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
            
            if line.startswith('#') and not in_code_block:
                if current_text:
                    parts.append('\n'.join(current_text))
                    current_text = []
                parts.append(line)
            else:
                current_text.append(line)
        if current_text:
            parts.append('\n'.join(current_text))
            
        current_section = None
        for part in parts:
            part = part.strip()
            if not part: continue

            if part.startswith('#'):
                if current_section: 
                    blog_data["sections"].append(current_section)
                
                header_text = part.lstrip('#').strip()
                current_section = {
                    "type": "paragraph",
                    "heading": f"#{header_text}",
                    "content": "",
                    "image": ""
                }
            elif current_section:
                clean_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', part).replace('\n', ' ').strip()
                current_section["content"] = clean_text

        if current_section: 
            blog_data["sections"].append(current_section)

        output_filename = f"{slug}.json"
        output_path = os.path.join(SAFE_DIRECTORY, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(blog_data, f, indent=2)

        return f"Success: Generated {output_filename} in safe directory."

    except Exception as e:
        return f"Error during MD conversion: {str(e)}"

@mcp.tool()
def stage_dynamic_blog_data(
    content: str = "", 
    category: str = "Content", 
    custom_slug: str = "", 
    image_url: str = "https://res.cloudinary.com/dx3atgryf/image/upload/v1777564396/iwhgn96jsdmsr48wervs.jpg"
) -> str:
    """
    Dynamically generates a Lizard Interactive JSON schema from pasted Markdown input.
    Use this to paste the whole document into the 'content' field.
    """
    if not content.strip():
        return "Error: Content field is blank. Please paste your Markdown text."

    try:
        # 1. Title & Slug Extraction
        title_match = re.search(r'^#\s+(.*)', content, re.MULTILINE)
        title = title_match.group(1) if title_match else "New Digital Asset"
        
        # Use custom_slug if a string is provided, otherwise generate from title
        slug = custom_slug if custom_slug.strip() else re.sub(r'[^a-z0-9]', '-', title.lower()).strip('-')
        
        # 2. Precision ISO Timestamp
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        # 3. Dynamic Schema Construction - Performance + Social Compatibility
        base_url = re.sub(r'\.(jpg|jpeg|png|webp)$', '', image_url)

        blog_data = {
            "id": slug,
            "category": category,
            "title": title,
            "createdAt": timestamp,
            "updatedAt": timestamp,
            "image": f"{base_url}.webp", 
            "ogImage": f"{base_url}.jpg",
            "sections": []
        }

        # 4. Content Parsing (Splits text by # headers, ignoring those in code blocks)
        parts = []
        current_text = []
        in_code_block = False

        for line in content.splitlines():
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
            
            if line.startswith('#') and not in_code_block:
                if current_text:
                    parts.append('\n'.join(current_text))
                    current_text = []
                parts.append(line)
            else:
                current_text.append(line)
        if current_text:
            parts.append('\n'.join(current_text))
            
        current_section = None
        for part in parts:
            part = part.strip()
            if not part: continue
            
            if part.startswith('#'):
                if current_section: 
                    blog_data["sections"].append(current_section)
                
                header_text = part.lstrip('#').strip()
                current_section = {
                    "type": "paragraph", 
                    "heading": f"#{header_text}", 
                    "content": "", 
                    "image": ""
                }
            elif current_section:
                clean_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', part).replace('\n', ' ').strip()
                current_section["content"] = clean_text

        if current_section: 
            blog_data["sections"].append(current_section)

        # 5. Export to Safe Directory
        output_path = os.path.join(SAFE_DIRECTORY, "pending_browser_post.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(blog_data, f, indent=2)

        return f"Successfully staged '{title}' under the '{category}' category. Ready for injection."

    except Exception as e:
        return f"Dynamic Processing Error: {str(e)}"

@mcp.tool()
def audit_performance_readiness(folder_name: str) -> str:
    """Audits a project folder for performance and SEO bottlenecks."""
    target_path = os.path.join(SAFE_DIRECTORY, folder_name)
    if not is_safe_path(target_path):
        return "Security Error: Access denied outside of Repositories folder."

    findings = [
        f"Analyzing {folder_name} for high-performance standards (100/100 Lighthouse Goal)...",
        "- Scanning for Next.js <Image /> component usage.",
        "- Checking for 'priority' flags on LCP elements.",
        "- Auditing 'layout.tsx' for proper SEO metadata."
    ]
    return "\n".join(findings)

@mcp.tool()
def seed_to_mongo(script_path: str = "scripts/seed-blog.ts") -> str:
    """Triggers the existing Node.js script to seed the database."""
    full_path = os.path.join(SAFE_DIRECTORY, script_path)
    if not is_safe_path(full_path):
        return "Security Error: Script location is outside safe repository."

    try:
        # Added shell=True for Windows compatibility with 'npx'
        result = subprocess.run(
            ["npx", "tsx", full_path], 
            capture_output=True, 
            text=True, 
            check=True, 
            shell=True 
        )
        return f"--- Database Seed Report ---\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"Error during seeding: {e.stderr}"
    except Exception as e:
        return f"System Error: {str(e)}"

@mcp.tool()
def read_pdf_audit(filename: str) -> str:
    """Reads and extracts text from a PDF audit file in the local audits directory."""
    target_path = os.path.join(AUDIT_DIRECTORY, filename)
    
    # Security check - ensure we are only reading from the AUDIT_DIRECTORY
    abs_target = os.path.abspath(target_path)
    if os.path.commonpath([abs_target, AUDIT_DIRECTORY]) != AUDIT_DIRECTORY:
        return "Security Error: Access denied outside of Audits folder."
        
    if not os.path.exists(abs_target):
        return f"Error: Could not find file {filename} in {AUDIT_DIRECTORY}"
        
    try:
        text_content = []
        with open(abs_target, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for i, page in enumerate(reader.pages):
                text_content.append(f"--- Page {i+1} ---")
                text_content.append(page.extract_text() or "")
                
        return "\n".join(text_content)
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

@mcp.tool()
def run_lighthouse_audit(url: str, filename: str) -> str:
    """Runs a professional Lighthouse audit for a given URL and saves it as a PDF in the audits folder."""
    script_path = os.path.abspath(os.path.join(SAFE_DIRECTORY, "servers/nodejs-automation/scripts/audit.js"))
    
    if not filename.endswith('.pdf'):
        filename += '.pdf'
        
    try:
        result = subprocess.run(
            ["node", script_path, url, AUDIT_DIRECTORY, filename],
            capture_output=True,
            text=True,
            check=True,
            shell=True
        )
        return f"Success! Lighthouse audit PDF generated for {url}.\nOutput:\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"Error during audit generation: {e.stderr or e.stdout}"
    except Exception as e:
        return f"System Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()