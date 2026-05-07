const fs = require("fs");
const path = require("path");
const puppeteer = require("puppeteer");

/**
 * Runs a Lighthouse audit and generates a high-quality PDF.
 * @param {string} url - The URL to audit.
 * @param {string} outputDir - The absolute path to save the folder.
 * @param {string} fileName - The name of the resulting PDF file.
 */
async function generateProfessionalPDF(url, outputDir, fileName) {
  console.log(`🚀 Starting RONDEV Lighthouse Audit for: ${url}\n`);

  // Ensure the target directory exists (creates it if it doesn't)
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
    console.log(`📁 Created directory: ${outputDir}`);
  }

  // Combine directory and filename
  const fullOutputPath = path.join(outputDir, fileName);

  // Dynamically import ESM-only packages inside the async function
  const { default: lighthouse } = await import("lighthouse");
  const chromeLauncher = await import("chrome-launcher");

  // 1. Launch headless Chrome for Lighthouse
  const chrome = await chromeLauncher.launch({ chromeFlags: ["--headless"] });

  const options = {
    logLevel: "warn",
    output: "html",
    onlyCategories: ["performance", "accessibility", "best-practices", "seo"],
    port: chrome.port,
  };

  // 2. Run the Lighthouse audit
  console.log("⏳ Running performance metrics (this may take a minute)...");
  const runnerResult = await lighthouse(url, options);

  // 3. Save the HTML report temporarily in the current working directory
  const htmlReport = runnerResult.report;
  const tempHtmlPath = `temp-${Date.now()}.html`;
  fs.writeFileSync(tempHtmlPath, htmlReport);
  console.log("✅ HTML data generated. Compiling into PDF...");

  await chrome.kill();

  // 4. Launch Puppeteer to render the HTML into a clean PDF
  const browser = await puppeteer.launch({ headless: "new" });
  const page = await browser.newPage();

  // Load the temporary HTML file
  const fileUrl = `file://${process.cwd()}/${tempHtmlPath}`;
  await page.goto(fileUrl, { waitUntil: "networkidle0" });

  // Force the screen CSS so gauges and colors look correct
  await page.emulateMediaType("screen");

  // 5. Generate the PDF and save it directly to your OneDrive path
  await page.pdf({
    path: fullOutputPath,
    format: "A4",
    printBackground: true,
    margin: {
      top: "20px",
      bottom: "20px",
      left: "20px",
      right: "20px",
    },
  });

  await browser.close();

  // 6. Clean up the temporary HTML file
  fs.unlinkSync(tempHtmlPath);

  console.log(`\n🎉 Success! Professional audit saved to:`);
  console.log(`👉 ${fullOutputPath}`);
}

// --- Execution ---
const targetUrl = process.argv[2] || "https://csjdm.gov.ph";

// Using double backslashes to safely format the Windows path in JavaScript
const targetDirectory =
  process.argv[3] || "C:\\Users\\ronan\\OneDrive\\Documents\\audits";
const outputFile = process.argv[4] || "CSJDM_Digital_Audit_RONDEV.pdf";

generateProfessionalPDF(targetUrl, targetDirectory, outputFile);
