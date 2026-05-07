# Lizard Interactive — Lighthouse AI Auditor

## How It Actually Works

**Gemini in Cursor IS the AI** — no separate API key or API calls needed.
The MCP tools are just mechanical workers that Gemini orchestrates.

When you type in Cursor:
```
@Lizard-Automation "test this url and provide insight? www.lizardinteractive.online"
```

Gemini automatically calls the tools in sequence:

```
1. run_lighthouse_audit(url)
      → Runs Lighthouse + Chrome headlessly
      → Saves report.html + report.json to C:\mcp-audits\<domain>\
      → Returns all scores + Core Web Vitals as text back to Gemini

2. Gemini reads the scores and writes its own professional analysis

3. save_audit_insights(url, insights_content)
      → Saves Gemini's analysis as <domain>_insights_<timestamp>.md
      → Same folder as the Lighthouse reports
```

Result folder:
```
C:\mcp-audits\
└── www_lizardinteractive_online\
    ├── www_lizardinteractive_online_audit.html   ← open in browser
    ├── www_lizardinteractive_online_audit.json   ← raw data
    └── www_lizardinteractive_online_insights_20250507_143022.md  ← AI analysis
```

---

## Setup (One-Time)

### 1. Node dependencies
```bash
npm install -g lighthouse chrome-launcher
```

### 2. Python dependencies (via uv, already in requirements.txt)
```
mcp
fastmcp
psutil
PyPDF2
beautifulsoup4
requests
reportlab
```

### 3. Place audit.js
Copy `scripts/audit.js` to:
```
C:\repositories\lizardinteractive-mcp-core\servers\nodejs-automation\scripts\audit.js
```

### 4. NO API KEY NEEDED
Gemini in Cursor is the AI. No GEMINI_API_KEY or ANTHROPIC_API_KEY required.

---

## Available Tools

| Tool | What it does |
|------|-------------|
| `run_lighthouse_audit(url)` | Runs Lighthouse, returns scores to Gemini |
| `save_audit_insights(url, content)` | Saves Gemini's analysis as Markdown |
| `list_audits()` | Shows all past audit folders |
| `read_pdf_audit(filename)` | Reads a PDF from audits folder |
| `save_code_review(filename, content)` | Saves code review Markdown |
| `get_system_report()` | CPU/RAM/Disk stats |

## File Structure

```
python-automation/
├── server.py
├── config.py
├── scripts/
│   └── audit.js              ← Node Lighthouse runner
├── tools/
│   ├── system.py
│   ├── audit.py
│   ├── blog.py
│   ├── database.py
│   ├── performance.py
│   └── lighthouse.py         ← run_lighthouse_audit, save_audit_insights, list_audits
└── utils/
    ├── security.py
    ├── markdown.py
    └── pdf_report.py
```