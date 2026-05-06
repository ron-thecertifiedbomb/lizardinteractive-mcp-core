// scripts/seed-blogs.ts
import { MongoClient } from "mongodb";
import * as dotenv from "dotenv";
import path from "path";
import fs from "fs";

// Ensure we find the .env.local in the root lizardinteractive-mcp-core folder
dotenv.config({ path: path.join(__dirname, "../.env.local") });

const uri = process.env.MONGODB_URI; // Use the key from your .env.local

// Debug line to verify it's loading correctly
console.log(
  "Checking URI:",
  uri ? "Found (starts with " + uri.substring(0, 15) + "...)" : "NOT FOUND",
);

interface BlogSection {
  type: string;
  heading: string;
  content: string;
  image: string;
}

interface BlogPost {
  id: string;
  category: string;
  title: string;
  sections: BlogSection[];
  createdAt: string;
  updatedAt: string;
}

async function seed() {
  if (!uri) {
    console.error("❌ MONGODB_URI is missing in .env.local");
    process.exit(1);
  }

  const client = new MongoClient(uri);

  try {
    // Look for the JSON produced by your Python scraper
    const jsonPath = path.join(__dirname, "./blog.json");
    if (!fs.existsSync(jsonPath)) {
      throw new Error(`Scraped file not found at ${jsonPath}`);
    }

    const rawData = fs.readFileSync(jsonPath, "utf-8");
    const data: BlogPost = JSON.parse(rawData);

    await client.connect();
    const db = client.db("lizrd_core");

    console.log(`⏳ Seeding article: ${data.id}...`);

    // Using upsert to maintain 100/100 data integrity
    await db
      .collection("articles")
      .updateOne({ id: data.id }, { $set: data }, { upsert: true });

    console.log("🚀 Lizard Engine: Data seeded successfully.");
  } catch (err) {
    console.error("❌ Seed Error:", err);
  } finally {
    await client.close();
    process.exit();
  }
}

seed();
