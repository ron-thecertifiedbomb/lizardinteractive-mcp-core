#!/usr/bin/env node

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

function printDirectoryStructure(dir, prefix = "") {
  const entries = fs.readdirSync(dir, { withFileTypes: true });

  for (const entry of entries) {
    const entryPath = path.join(dir, entry.name);
    console.log(`${prefix}- ${entry.name}`);

    if (entry.isDirectory()) {
      printDirectoryStructure(entryPath, prefix + "  ");
    }
  }
}

printDirectoryStructure(process.cwd());
