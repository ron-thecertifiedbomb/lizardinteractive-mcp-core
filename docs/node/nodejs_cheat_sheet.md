# 🟢 Node.js & NPM Cheat Sheet

Welcome to your personal Node.js command-line cheatcode list! This document saves the terminal commands used to manage the Javascript side of the Lizard MCP Core repository (like your Lighthouse runner).

---

## 1. Run a Node.js Script

**The Cheatcode:**
```bash
node <script_name.js>
```

**What it does:** 
Executes a JavaScript file using the Node.js runtime. For example, running your Lighthouse audit script.

**How it works (Line-by-Line Breakdown):**
*   `node`  
    Calls the Node.js runtime environment.
*   `<script_name.js>`  
    The JavaScript file you want to execute (for example, `servers/nodejs-automation/scripts/audit.js`).

---

## 2. Manage Node.js Dependencies

**The Cheatcode (Add a new package):**
```bash
npm install <package_name>
```

**What it does:** 
Downloads and installs a new Node.js package (like `puppeteer` or `lighthouse`) into your project's `node_modules` folder and updates your `package.json`.

**The Cheatcode (Install all project dependencies):**
```bash
npm install
```
**What it does:** Reads your `package.json` file and downloads all the required packages for your project. You usually run this once when you first set up a repository.
