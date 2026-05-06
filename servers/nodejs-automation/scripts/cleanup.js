import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Equivalent of __dirname in ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const log = (msg) => console.log(`🧹 ${msg}`);

try {
  // 1. Kill node processes (Windows)
  if (process.platform === 'win32') {
    log('Killing node processes...');
    execSync('taskkill /F /IM node.exe', { stdio: 'ignore' });
  }

  // 2. Remove node_modules
  const nodeModulesPath = path.join(__dirname, 'node_modules');
  if (fs.existsSync(nodeModulesPath)) {
    log('Removing node_modules...');
    fs.rmSync(nodeModulesPath, { recursive: true, force: true });
  }

  // 3. Remove yarn.lock
  const yarnLockPath = path.join(__dirname, 'yarn.lock');
  if (fs.existsSync(yarnLockPath)) {
    log('Removing yarn.lock...');
    fs.rmSync(yarnLockPath);
  }

  // 4. Clear Yarn cache
  log('Clearing yarn cache...');
  execSync('yarn cache clean', { stdio: 'inherit' });

  // 5. Reinstall dependencies
  log('Installing dependencies...');
  execSync('yarn install', { stdio: 'inherit' });

  log('✅ Cleanup completed successfully!');
} catch (err) {
  console.error('❌ Cleanup failed:', err.message);
  process.exit(1);
}
