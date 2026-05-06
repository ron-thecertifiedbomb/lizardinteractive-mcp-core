const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const repoName = "landing-page";
const localPath = path.join(__dirname, repoName);

// 1. Create project folder
if (!fs.existsSync(localPath)) fs.mkdirSync(localPath);
console.log("Created folder:", localPath);

// 2. Initialize Git
execSync("git init", { cwd: localPath, stdio: "inherit" });
console.log("Initialized Git.");

// 3. Create package.json
const packageJson = {
  name: repoName,
  version: "1.0.0",
  private: true,
  scripts: {
    dev: "vite",
    build: "vite build",
    preview: "vite preview"
  },
  dependencies: {
    react: "^18.2.0",
    "react-dom": "^18.2.0",
    "@radix-ui/react-toast": "^1.0.6",
    "@radix-ui/react-switch": "^1.0.6",
    "@supabase/supabase-js": "^2.0.0"
  },
  devDependencies: {
    vite: "^5.0.0",
    typescript: "^5.2.0",
    tailwindcss: "^3.3.0",
    autoprefixer: "^10.4.0",
    postcss: "^8.4.0",
    "@vitejs/plugin-react": "^4.0.0"
  }
};
fs.writeFileSync(path.join(localPath, "package.json"), JSON.stringify(packageJson, null, 2));

// 4. Create basic folder structure
const srcPath = path.join(localPath, "src");
const componentsPath = path.join(srcPath, "components");
const libPath = path.join(srcPath, "lib");
[ srcPath, componentsPath, libPath ].forEach(p => fs.mkdirSync(p, { recursive: true }));

// 5. Create minimal files
fs.writeFileSync(path.join(localPath, "vite.config.ts"), `import { defineConfig } from 'vite'; import react from '@vitejs/plugin-react'; export default defineConfig({ plugins: [react()] });`);
fs.writeFileSync(path.join(localPath, "tsconfig.json"), `{ "compilerOptions": { "target": "ESNext", "lib": ["DOM","ESNext"], "jsx": "react-jsx" }, "include": ["src"] }`);
fs.writeFileSync(path.join(localPath, "tailwind.config.js"), `export default { content: ['./index.html','./src/**/*.{ts,tsx}'], theme: { extend: {} }, plugins: [] }`);
fs.writeFileSync(path.join(localPath, "postcss.config.js"), `module.exports = { plugins: { tailwindcss: {}, autoprefixer: {} } }`);
fs.writeFileSync(path.join(localPath, "index.html"), `<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>Landing Page Radix TS</title></head><body><div id='root'></div><script type='module' src='/src/main.tsx'></script></body></html>`);

// 6. Create src files
fs.writeFileSync(path.join(srcPath, "main.tsx"), `
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode><App /></React.StrictMode>
);
`);
fs.writeFileSync(path.join(srcPath, "index.css"), `@tailwind base;@tailwind components;@tailwind utilities;`);
fs.writeFileSync(path.join(libPath, "supabaseClient.ts"), `import { createClient } from '@supabase/supabase-js'; export const supabase = createClient('https://xyz.supabase.co','public-anon-key');`);

// 7. Create App.tsx with basic components
fs.writeFileSync(path.join(srcPath, "App.tsx"), `
import React from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Carousel from './components/Carousel';
import Cards from './components/Cards';
import Footer from './components/Footer';
import ToastDemo from './components/ToastDemo';

export default function App() {
  return (
    <div className="font-sans">
      <Navbar />
      <Hero />
      <Carousel />
      <Cards />
      <ToastDemo />
      <Footer />
    </div>
  );
}
`);

// 8. Create minimal components
const basicComponents = {
  "Navbar.tsx": `import React from 'react'; export default function Navbar(){ return <nav className="p-6 bg-gray-800 text-white">Logo | Navbar</nav>; }`,
  "Hero.tsx": `import React from 'react'; export default function Hero(){ return <section className="text-center py-20 bg-gray-100"><h1 className="text-4xl font-bold">Hero Section</h1></section>; }`,
  "Carousel.tsx": `import React from 'react'; export default function Carousel(){ return <section className="py-10 px-6 text-center">Carousel placeholder</section>; }`,
  "Cards.tsx": `import React from 'react'; export default function Cards(){ return <section className="py-10 px-6 grid grid-cols-1 md:grid-cols-3 gap-6"><div className="p-6 bg-white shadow rounded">Card 1</div><div className="p-6 bg-white shadow rounded">Card 2</div><div className="p-6 bg-white shadow rounded">Card 3</div></section>; }`,
  "Footer.tsx": `import React from 'react'; export default function Footer(){ return <footer className="p-6 bg-gray-800 text-white text-center">&copy; 2025 Landing Page</footer>; }`,
  "ToastDemo.tsx": `import * as Toast from '@radix-ui/react-toast'; import { useState } from 'react'; export default function ToastDemo(){ const [open,setOpen]=useState(false); return (<div className="text-center py-10"><button onClick={()=>setOpen(true)} className="px-4 py-2 bg-blue-600 text-white rounded">Show Toast</button><Toast.Provider><Toast.Root open={open} onOpenChange={setOpen} className="bg-gray-800 text-white p-4 rounded mt-4 inline-block"><Toast.Title>Item added</Toast.Title></Toast.Root></Toast.Provider></div>); }`,
  "ThemeToggle.tsx": `import * as Switch from '@radix-ui/react-switch'; import { useState,useEffect } from 'react'; export default function ThemeToggle(){ const [dark,setDark]=useState(false); useEffect(()=>{ if(dark) document.documentElement.classList.add('dark'); else document.documentElement.classList.remove('dark'); },[dark]); return (<Switch.Root className="w-12 h-6 bg-gray-300 dark:bg-gray-700 rounded-full relative" checked={dark} onCheckedChange={setDark}><Switch.Thumb className="block w-6 h-6 bg-white rounded-full shadow translate-x-0 transition-transform" /></Switch.Root>); }`
};

for (const [file, content] of Object.entries(basicComponents)) {
  fs.writeFileSync(path.join(componentsPath, file), content);
}

// 9. Commit all files
execSync("git add .", { cwd: localPath });
execSync('git commit -m "Initial full project setup"', { cwd: localPath });
console.log("Committed full project.");

// 10. Create GitHub repo using gh CLI and push
try {
  execSync(`gh repo create ${repoName} --public --source=${localPath} --remote=origin --push`, { stdio: "inherit" });
  console.log("Full project repo created and pushed to GitHub successfully!");
} catch (error) {
  console.error("Failed to create GitHub repo:", error.message);
}