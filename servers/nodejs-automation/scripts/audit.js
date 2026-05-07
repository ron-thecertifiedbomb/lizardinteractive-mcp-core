/**
 * audit.js — Lizard Interactive Lighthouse Runner
 * Called by the Python MCP server via subprocess.
 *
 * Usage:
 *   node audit.js <url> <outputDir> <filename>
 *
 * Install once:
 *   npm install -g lighthouse puppeteer-core
 */

const lighthouse = require("lighthouse");
const chromeLauncher = require("chrome-launcher");
const fs = require("fs");
const path = require("path");

async function run() {
  const [, , url, outputDir, filename] = process.argv;

  if (!url || !outputDir || !filename) {
    console.error("Usage: node audit.js <url> <outputDir> <filename>");
    process.exit(1);
  }

  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const chrome = await chromeLauncher.launch({
    chromeFlags: ["--headless", "--no-sandbox", "--disable-gpu"],
  });

  try {
    const options = {
      logLevel: "error",
      output: ["json", "html"],
      onlyCategories: ["performance", "accessibility", "best-practices", "seo"],
      port: chrome.port,
    };

    const runnerResult = await lighthouse(url, options);

    // ── Save raw JSON report ───────────────────────────────────────────────
    const jsonPath = path.join(outputDir, `${filename}.json`);
    fs.writeFileSync(jsonPath, runnerResult.report[0], "utf8");

    // ── Save HTML report (readable in browser) ────────────────────────────
    const htmlPath = path.join(outputDir, `${filename}.html`);
    fs.writeFileSync(htmlPath, runnerResult.report[1], "utf8");

    // ── Extract scores for stdout (Python reads this) ─────────────────────
    const cats = runnerResult.lhr.categories;
    const audits = runnerResult.lhr.audits;

    const scores = {
      performance: cats["performance"]?.score ?? null,
      accessibility: cats["accessibility"]?.score ?? null,
      best_practices: cats["best-practices"]?.score ?? null,
      seo: cats["seo"]?.score ?? null,
      lcp: audits["largest-contentful-paint"]?.displayValue ?? "N/A",
      tbt: audits["total-blocking-time"]?.displayValue ?? "N/A",
      cls: audits["cumulative-layout-shift"]?.displayValue ?? "N/A",
      fcp: audits["first-contentful-paint"]?.displayValue ?? "N/A",
      tti: audits["interactive"]?.displayValue ?? "N/A",
      speed_index: audits["speed-index"]?.displayValue ?? "N/A",
    };

    // Top opportunities
    const opportunities = [];
    for (const [key, audit] of Object.entries(audits)) {
      if (audit.details?.type === "opportunity") {
        const savings = audit.details?.overallSavingsMs ?? 0;
        if (savings > 0) {
          opportunities.push({
            title: audit.title,
            savings: `${Math.round(savings)}ms`,
            rawSavings: savings,
            score: audit.score,
          });
        }
      }
    }
    scores.opportunities = opportunities
      .sort((a, b) => b.rawSavings - a.rawSavings)
      .map(({ rawSavings, ...rest }) => rest)
      .slice(0, 5);

    // Failed binary audits (diagnostics)
    const diagnostics = [];
    for (const [key, audit] of Object.entries(audits)) {
      if (
        audit.score !== null &&
        audit.score < 1.0 &&
        audit.scoreDisplayMode === "binary"
      ) {
        diagnostics.push({
          title: audit.title,
          description: audit.description ?? "",
          score: audit.score,
        });
      }
    }
    scores.diagnostics = diagnostics.slice(0, 8);

    // Output JSON to stdout — Python captures this
    console.log(JSON.stringify({ success: true, jsonPath, htmlPath, scores }));
  } finally {
    await chrome.kill();
  }
}

run().catch((err) => {
  console.error(JSON.stringify({ success: false, error: err.message }));
  process.exit(1);
});
