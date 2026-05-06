#!/usr/bin/env node
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function printDir(dirPath, prefix = "", depth = 0, maxDepth = 5) {
  if (depth > maxDepth) return;

  const items = fs.readdirSync(dirPath);
  items.forEach((item, i) => {
    const isLast = i === items.length - 1;
    const fullPath = path.join(dirPath, item);
    const stat = fs.statSync(fullPath);

    const line = `${prefix}${isLast ? "└──" : "├──"} ${item}`;
    console.log(line);

    if (
      stat.isDirectory() &&
      !["node_modules", ".git", ".next"].includes(item)
    ) {
      printDir(
        fullPath,
        prefix + (isLast ? "    " : "│   "),
        depth + 1,
        maxDepth
      );
    }
  });
}

printDir(process.cwd());
