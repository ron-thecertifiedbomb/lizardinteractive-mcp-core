#!/usr/bin/env node

import { execSync } from "child_process";
import fs from "fs";

const run = (cmd) => execSync(cmd, { stdio: "inherit" });

// Prevent overwrite
if (fs.existsSync("my-app")) {
  console.error("❌ Directory 'my-app' already exists. Remove it first.");
  process.exit(1);
}

// 1. Create Vite React TypeScript project
console.log("🚀 Creating Vite React TypeScript project...");
run(`npm create vite@latest my-app -- --template react-ts`);
process.chdir("my-app");

// 2. Install dependencies
console.log("📦 Installing Tailwind, Radix, and Shadcn/UI...");
run(`npm install tailwindcss postcss autoprefixer @radix-ui/react-navigation-menu @radix-ui/react-accordion class-variance-authority clsx tailwind-variants lucide-react`);

console.log("🎨 Initializing Shadcn/UI...");
run(`npx shadcn-ui@latest init -y`);

// 3. Tailwind config
console.log("⚙️ Setting up Tailwind CSS...");
run(`npx tailwindcss init -p`);

fs.writeFileSync(
  "tailwind.config.cjs",
  `/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./node_modules/@shadcn/ui/**/*.{js,ts,jsx,tsx}"
  ],
  theme: { extend: {} },
  plugins: [],
};`
);

fs.writeFileSync(
  "src/index.css",
  `@tailwind base;
@tailwind components;
@tailwind utilities;
`
);

// 4. Components folder
fs.mkdirSync("src/components", { recursive: true });
console.log("🎯 Creating Shadcn-based components...");

// Navbar
fs.writeFileSync(
  "src/components/Navbar.tsx",
  `import { NavigationMenu, NavigationMenuList, NavigationMenuItem, NavigationMenuLink } from "@/components/ui/navigation-menu"

export function Navbar() {
  return (
    <NavigationMenu className="p-4 bg-white shadow">
      <NavigationMenuList>
        <NavigationMenuItem><NavigationMenuLink href="#">Home</NavigationMenuLink></NavigationMenuItem>
        <NavigationMenuItem><NavigationMenuLink href="#">About</NavigationMenuLink></NavigationMenuItem>
      </NavigationMenuList>
    </NavigationMenu>
  );
}`
);

// Hero
fs.writeFileSync(
  "src/components/Hero.tsx",
  `import { Button } from "@/components/ui/button"

export function Hero() {
  return (
    <section className="bg-gray-100 py-20 text-center">
      <h1 className="text-5xl font-bold mb-4">Welcome to My App</h1>
      <p className="text-lg text-gray-600 mb-6">This is a beautiful hero section built with Tailwind + Shadcn.</p>
      <Button size="lg">Get Started</Button>
    </section>
  );
}`
);

// Carousel
fs.writeFileSync(
  "src/components/Carousel.tsx",
  `export function Carousel() {
  const items = ["1", "2", "3"];
  return (
    <div className="w-full overflow-x-auto flex gap-4 p-4">
      {items.map((item) => (
        <div key={item} className="min-w-[300px] bg-gray-200 h-48 flex items-center justify-center text-2xl font-bold rounded-lg">
          Slide {item}
        </div>
      ))}
    </div>
  );
}`
);

// Cards
fs.writeFileSync(
  "src/components/Cards.tsx",
  `import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"

export function Cards() {
  return (
    <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-4">
      <Card><CardHeader><CardTitle>Card 1</CardTitle></CardHeader><CardContent>Content 1</CardContent></Card>
      <Card><CardHeader><CardTitle>Card 2</CardTitle></CardHeader><CardContent>Content 2</CardContent></Card>
      <Card><CardHeader><CardTitle>Card 3</CardTitle></CardHeader><CardContent>Content 3</CardContent></Card>
    </div>
  );
}`
);

// Accordion
fs.writeFileSync(
  "src/components/AccordionSection.tsx",
  `import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@/components/ui/accordion"

export function AccordionSection() {
  return (
    <div className="p-6">
      <Accordion type="single" collapsible>
        <AccordionItem value="item-1"><AccordionTrigger>Item 1</AccordionTrigger><AccordionContent>Content 1</AccordionContent></AccordionItem>
        <AccordionItem value="item-2"><AccordionTrigger>Item 2</AccordionTrigger><AccordionContent>Content 2</AccordionContent></AccordionItem>
      </Accordion>
    </div>
  );
}`
);

// App.tsx
fs.writeFileSync(
  "src/App.tsx",
  `import "./index.css"
import { Navbar } from "@/components/Navbar"
import { Hero } from "@/components/Hero"
import { Carousel } from "@/components/Carousel"
import { Cards } from "@/components/Cards"
import { AccordionSection } from "@/components/AccordionSection"

function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <Hero />
      <Carousel />
      <Cards />
      <AccordionSection />
    </div>
  )
}

export default App`
);

console.log("✅ Shadcn Vite React TS setup complete!");
console.log("Next steps:\n1. cd my-app\n2. npm install\n3. npm run dev");
