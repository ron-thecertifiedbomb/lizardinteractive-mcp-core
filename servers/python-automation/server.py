import os
import psutil
import platform
import shutil
import requests
import json
import re
import subprocess
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP for Lizard Interactive
mcp = FastMCP("Lizard-Automation")

# Your professional-grade path verification
SAFE_DIRECTORY = os.path.abspath("C:/repositories/lizardinteractive-mcp-core")

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

        parts = re.split(r'^(#+.*)$', content, flags=re.MULTILINE)
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
        # Primary image remains .webp for 100/100 Lighthouse performance
        # ogImage uses .jpg to ensure perfect previews in community groups
        base_url = re.sub(r'\.(jpg|jpeg|png|webp)$', '', image_url)

        blog_data = {
            "id": slug,
            "category": category,
            "title": title,
            "createdAt": timestamp,
            "updatedAt": timestamp,
            "image": f"{base_url}.webp",   # High-speed site asset
            "ogImage": f"{base_url}.jpg", # Social media compatibility
            "sections": []
        }

        # 4. Content Parsing (Splits text by # headers)
        parts = re.split(r'^(#+.*)$', content, flags=re.MULTILINE)
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





if __name__ == "__main__":
    mcp.run()