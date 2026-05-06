// scripts/add-file-header-comments.js
const fs = require('fs');
const path = require('path');

const targetDir = path.resolve(__dirname, '../src/__tests__');

fs.readdirSync(targetDir).forEach((file) => {
  if (file.endsWith('.test.tsx') || file.endsWith('.test.ts')) {
    const filePath = path.join(targetDir, file);
    const content = fs.readFileSync(filePath, 'utf8');

    const headerComment = `// src/__tests__/${file}`;
    if (!content.startsWith(headerComment)) {
      const updated = `${headerComment}\n\n${content}`;
      fs.writeFileSync(filePath, updated);
      console.log(`✔️ Added header to ${file}`);
    }
  }
});
