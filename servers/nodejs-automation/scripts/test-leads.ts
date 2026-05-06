// scripts/test-leads.ts

import { analyzeLead } from "../lib/gemini";
import clientPromise from "../lib/mongodb";
import { scrapeJobbers } from "../lib/scraper";

async function localTest() {
  console.log("🔍 Starting local scrape test...");

  try {
    // 1. Scrape
    const rawJobs = await scrapeJobbers();
    console.log(`📡 Found ${rawJobs.length} jobs on the page.`);

    if (rawJobs.length === 0) {
      console.log(
        "⚠️ No jobs found. Check if the selector in lib/scraper matches the site.",
      );
      return;
    }

    // 2. Connect
    const client = await clientPromise;
    const db = client.db("lizrd_interactive");
    const collection = db.collection("leads");

    // 3. Process first 2 jobs only (to save Gemini tokens during testing)
    for (const job of rawJobs.slice(0, 2)) {
      console.log(`🤖 Analyzing: ${job.title}...`);

      const analysis = await analyzeLead(job.title, job.description);
      console.log(`📊 Score: ${analysis.score}/10`);

      if (analysis.score >= 7) {
        await collection.updateOne(
          { link: job.link },
          {
            $set: {
              ...job,
              ...analysis,
              status: "test",
              createdAt: new Date(),
            },
          },
          { upsert: true },
        );
        console.log("✅ Saved to MongoDB!");
      } else {
        console.log("⏩ Score too low, skipping save.");
      }
    }
  } catch (error) {
    console.error("❌ Test failed:", error);
  } finally {
    process.exit();
  }
}

localTest();
