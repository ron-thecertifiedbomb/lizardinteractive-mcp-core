#!/usr/bin/env node

const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const projectRoot = path.resolve(__dirname, "..");

try {
  console.log("🔁 Deleting existing .git directory...");
  fs.rmSync(path.join(projectRoot, ".git"), { recursive: true, force: true });

  console.log("🔧 Reinitializing Git...");
  execSync("git init", { cwd: projectRoot, stdio: "inherit" });

  console.log("➕ Adding all files...");
  execSync("git add .", { cwd: projectRoot, stdio: "inherit" });

  console.log("✅ Creating new initial commit...");
  execSync('git commit -m "Initial commit"', {
    cwd: projectRoot,
    stdio: "inherit",
  });

  console.log("🎉 Git history has been reset.");
} catch (error) {
  console.error("❌ Error resetting Git:", error.message);
}
