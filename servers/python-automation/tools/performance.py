import os
import re
from mcp.server.fastmcp import FastMCP
from config import SAFE_DIRECTORY
from utils.security import is_safe_path


def register(mcp: FastMCP):

    @mcp.tool()
    def audit_performance_readiness(folder_name: str) -> str:
        """Audits a project folder for performance and SEO bottlenecks."""
        target_path = os.path.join(SAFE_DIRECTORY, folder_name)
        if not is_safe_path(target_path):
            return "Security Error: Access denied outside of Repositories folder."

        findings = [
            f"Analyzing {folder_name} for high-performance standards (100/100 Lighthouse Goal)..."
        ]

        # Perform an actual static scan of the React/Next.js codebase
        img_count, prio_count = 0, 0
        for root, dirs, files in os.walk(target_path):
            dirs[:] = [d for d in dirs if d not in {"node_modules", ".next", ".git"}]
            for file in files:
                if file.endswith(('.tsx', '.jsx')):
                    with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        img_count += len(re.findall(r'<Image\b', content))
                        prio_count += len(re.findall(r'<Image\b[^>]*\bpriority\b', content))

        findings.append(f"- Scanned Next.js files: found {img_count} <Image /> components.")
        findings.append(f"- Checked LCP elements: {prio_count} 'priority' flags detected.")
        findings.append("- Reminder: Manually audit 'layout.tsx' for proper SEO metadata.")

        return "\n".join(findings)