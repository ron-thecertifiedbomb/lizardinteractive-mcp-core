const { MongoClient } = require("mongodb");
require("dotenv").config(); // Ensure you have your .env loaded

// Use your verified Standard URI for local stability
const URI =
  "mongodb://lizrd_architect:Ronan_1980@cluster0-shard-00-00.gdgvcmj.mongodb.net:27017,cluster0-shard-00-01.gdgvcmj.mongodb.net:27017,cluster0-shard-00-02.gdgvcmj.mongodb.net:27017/lizrd_core?ssl=true&replicaSet=atlas-gdgvcm-shard-0&authSource=admin&retryWrites=true&w=majority";

async function loadPantry() {
  const client = new MongoClient(URI);

  const leads = [
    {
      name: "Budji + Royal Architecture",
      email: "info@budjiroyal.com",
      websiteUrl: "https://www.budjiroyal.com",
      industry: "Architecture",
      contacted: false,
      createdAt: new Date(),
    },
    {
      name: "KM Interior Design Manila",
      email: "hello@kminteriordesign.com",
      websiteUrl: "https://kminteriordesign.com",
      industry: "Interior Design",
      contacted: false,
      createdAt: new Date(),
    },
    {
      name: "W.V. Coscolluela & Associates",
      email: "wvca@wvcoscolluela.com",
      websiteUrl: "https://www.wvcoscolluela.com",
      industry: "Architecture",
      contacted: false,
      createdAt: new Date(),
    },
  ];

  try {
    console.log("--- INITIALIZING HANDSHAKE ---");
    await client.connect();
    console.log("✔ CONNECTION ESTABLISHED");

    const db = client.db("prospects");
    const result = await db.collection("prospects").insertMany(leads);

    console.log(
      `✔ SUCCESS: ${result.insertedCount} leads injected into the pantry.`,
    );
    console.log("--- OPERATION COMPLETE ---");
  } catch (error) {
    console.error("✖ CRITICAL FAILURE:", error.message);
    if (error.message.includes("ENOTFOUND")) {
      console.log(
        "\n[LIZRD_ADVICE]: Your local DNS is still blocking the shards.",
      );
      console.log(
        "Please use the Atlas Web UI to bypass this local restriction.",
      );
    }
  } finally {
    await client.close();
  }
}

loadPantry();
