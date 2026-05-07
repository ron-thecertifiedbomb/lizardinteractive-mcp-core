"""
tools/lighthouse.py — Lighthouse audit tools for the lizard-automation MCP server.

HOW IT ACTUALLY WORKS:
  Gemini (in Cursor) is the AI brain — no separate API call needed.
  These tools just do the mechanical work and return data back to Gemini.

  When you type:
    @lizard-automation "test this url and provide insight? www.lizardinteractive.online"

  Gemini calls the tools in this order automatically:
    1. run_lighthouse_audit(url)   → runs Lighthouse, saves HTML/JSON, returns scores as text
    2. save_audit_insights(url, insights_content)  → Gemini writes its own analysis to .md

  The folder is: C:\\mcp-audits\\<safe_domain>\\
"""

import os
import re
import json
import shutil
import subprocess
from datetime import datetime, timezone
from urllib.parse import urlparse

from mcp.server.fastmcp import FastMCP
from config import SAFE_DIRECTORY, AUDIT_DIRECTORY

_AUDIT_JS = os.path.abspath(
    os.path.join(SAFE_DIRECTORY, "servers/nodejs-automation/scripts/audit.js")
)
_AUDIT_JS_LOCAL = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "scripts", "audit.js")
)


def _slugify(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", text).strip("_")


def _normalize_url(url: str) -> str:
    if not url.startswith("http://") and not url.startswith("https://"):
        url = f"https://{url}"
        
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Invalid URL scheme. Only HTTP and HTTPS are allowed.")
        
    # Strip fragments and trailing slashes, but retain query parameters
    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
    if parsed.query:
        clean_url += f"?{parsed.query}"
    return clean_url


def _get_safe_domain(url: str) -> str:
    domain = urlparse(url).netloc or url
    return _slugify(domain)


def _audit_js_path() -> str:
    if os.path.exists(_AUDIT_JS):
        return _AUDIT_JS
    if os.path.exists(_AUDIT_JS_LOCAL):
        return _AUDIT_JS_LOCAL
    raise FileNotFoundError(
        f"audit.js not found.\nExpected at:\n"
        f"  {_AUDIT_JS}\n  {_AUDIT_JS_LOCAL}\n\n"
        f"Copy scripts/audit.js to one of those locations."
    )


def _pct(score) -> str:
    if score is None:
        return "N/A"
    return f"{int(round(float(score) * 100))}%"


def _label(score) -> str:
    if score is None:
        return "N/A"
    s = float(score)
    if s >= 0.90: return "GOOD"
    if s >= 0.50: return "NEEDS WORK"
    return "POOR"


def _generate_summary_report(url: str, url_dir: str, lh_out: dict, from_cache: bool = False) -> str:
    """Generates a formatted text summary from the Lighthouse output JSON."""
    scores = lh_out["scores"]
    html_path = lh_out.get("htmlPath", "")
    json_path = lh_out.get("jsonPath", "")

    opps = scores.get("opportunities", [])
    diags = scores.get("diagnostics", [])

    opp_lines = "\n".join(
        f"  * {o['title']} — save ~{o['savings']} (score: {_pct(o.get('score'))})"
        for o in opps
    ) or "  None detected"

    diag_lines = "\n".join(f"  * {d['title']}" for d in diags) or "  None detected"

    cache_status = "(from cache)" if from_cache else ""

    summary = f"""Lighthouse Audit Complete {cache_status}
URL     : {url}
Folder  : {url_dir}
HTML    : {html_path}
JSON    : {json_path}

OVERALL SCORES
  Performance    : {_pct(scores.get('performance')):<6}  {_label(scores.get('performance'))}
  Accessibility  : {_pct(scores.get('accessibility')):<6}  {_label(scores.get('accessibility'))}
  Best Practices : {_pct(scores.get('best_practices')):<6}  {_label(scores.get('best_practices'))}
  SEO            : {_pct(scores.get('seo')):<6}  {_label(scores.get('seo'))}

CORE WEB VITALS
  LCP  (Largest Contentful Paint) : {scores.get('lcp', 'N/A')}   target < 2.5s
  TBT  (Total Blocking Time)      : {scores.get('tbt', 'N/A')}   target < 200ms
  CLS  (Cumulative Layout Shift)  : {scores.get('cls', 'N/A')}   target < 0.1

TOP OPPORTUNITIES (potential ms savings)
{opp_lines}

Now analyze these results and call save_audit_insights(url="{url}", insights_content="...") to save your report."""
    return summary.strip()

def register(mcp: FastMCP):

    @mcp.tool()
    def run_lighthouse_audit(url: str, filename: str = "", force: bool = False) -> str:
        """
        Runs a Lighthouse performance audit on a URL.
        Saves HTML + JSON reports to a dedicated folder inside the audits directory.
        Returns a full text summary of all scores and metrics so the AI can analyze them.

        Use this first when asked to audit, test, or review any website.
        After calling this, write your analysis using save_audit_insights().
        """
        try:
            url = _normalize_url(url)
        except ValueError as e:
            return f"Input Error: {e}"
        safe_domain = _get_safe_domain(url)
        url_dir = os.path.join(AUDIT_DIRECTORY, safe_domain)
        os.makedirs(url_dir, exist_ok=True)

        if not filename:
            filename = f"{safe_domain}_audit"
        filename = _slugify(filename)
        summary_path = os.path.join(url_dir, f"{filename}.summary.json")

        # Check for a recent cached audit (less than 24 hours old)
        if not force and os.path.exists(summary_path):
            mod_time = datetime.fromtimestamp(os.path.getmtime(summary_path), tz=timezone.utc)
            if (datetime.now(timezone.utc) - mod_time).total_seconds() < 86400:
                try:
                    with open(summary_path, 'r', encoding='utf-8') as f:
                        lh_out = json.load(f)
                    if "scores" in lh_out:
                        # Return the cached summary
                        return _generate_summary_report(url, url_dir, lh_out, from_cache=True)
                except (json.JSONDecodeError, IOError):
                    # If cache is corrupt or unreadable, proceed to a fresh run
                    pass

        try:
            audit_js = _audit_js_path()
        except FileNotFoundError as e:
            return f"Setup Error: {e}"

        node_path = shutil.which("node")
        if not node_path:
            return "System Error: 'node' command not found. Is Node.js installed and in your PATH?"

        try:
            result = subprocess.run(
                [node_path, audit_js, url, url_dir, filename],
                capture_output=True,
                text=True,
                timeout=180,
                shell=False,
            )
        except subprocess.TimeoutExpired:
            return "Error: Lighthouse timed out after 3 minutes. Check that Chrome is installed."
        except Exception as e:
            return f"System Error running Lighthouse: {e}"

        if result.returncode != 0:
            return (
                f"Lighthouse Error (exit code {result.returncode}):\n"
                f"{result.stderr.strip()}\n\n"
                f"Make sure you have run:  npm install -g lighthouse\n"
                f"And that Chrome is installed."
            )

        stdout = result.stdout.strip()

        # Extract the JSON payload safely, ignoring potential Chrome Launcher warnings
        try:
            json_start = stdout.find("{")
            json_end = stdout.rfind("}")
            if json_start == -1 or json_end == -1:
                raise ValueError("No JSON object found")
            json_str = stdout[json_start:json_end+1]
            lh_out = json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            return f"Could not parse Lighthouse output.\nRaw:\n{stdout[:800]}\nStderr:\n{result.stderr[:400]}"

        # Save the successful raw output to the cache file
        try:
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(lh_out, f)
        except IOError:
            # This is non-critical, just means we can't cache for next time
            pass

        # Generate and return the fresh summary report
        return _generate_summary_report(url, url_dir, lh_out, from_cache=False)

    @mcp.tool()
    def save_audit_insights(url: str, insights_content: str) -> str:
        """
        Saves the AI-generated Lighthouse audit insights as a Markdown file
        in the audit folder for that URL.

        Call this AFTER run_lighthouse_audit() with your complete professional analysis.
        The insights_content should include: executive summary, critical issues,
        quick wins, priority actions, and next steps for the client.
        """
        url = _normalize_url(url)
        safe_domain = _get_safe_domain(url)
        url_dir = os.path.join(AUDIT_DIRECTORY, safe_domain)
        os.makedirs(url_dir, exist_ok=True)

        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_domain}_insights_{ts}.md"
        out_path = os.path.join(url_dir, filename)

        try:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(f"# Audit Insights - {url}\n\n")
                f.write(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n")
                f.write("---\n\n")
                f.write(insights_content)
            return f"Insights saved to: {out_path}\nFolder: {url_dir}"
        except Exception as e:
            return f"File System Error: {str(e)}"

    @mcp.tool()
    def list_audits() -> str:
        """
        Lists all audit folders and their files in the audits directory.
        Use this when asked to show previous audits or audit history.
        """
        if not os.path.exists(AUDIT_DIRECTORY):
            return f"Audits directory does not exist yet: {AUDIT_DIRECTORY}"

        output = [f"AUDIT HISTORY - {AUDIT_DIRECTORY}", "=" * 60]
        found = False

        for folder in sorted(os.listdir(AUDIT_DIRECTORY), reverse=True):
            full = os.path.join(AUDIT_DIRECTORY, folder)
            if not os.path.isdir(full):
                continue
            found = True
            mtime = datetime.fromtimestamp(os.path.getmtime(full), tz=timezone.utc)
            output.append(f"\n{folder}  ({mtime.strftime('%Y-%m-%d %H:%M')} UTC)")
            for f in sorted(os.listdir(full)):
                output.append(f"   {f}")

        if not found:
            return "No audits found yet. Run run_lighthouse_audit() to get started."

        return "\n".join(output)