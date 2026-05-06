// scripts/test-rss.ts
async function checkFeed() {
  const urlsToTest = [
    "https://www.jobbers.io/feed",
    "https://www.jobbers.io/en/projects/feed",
    "https://www.jobbers.ma/feed",
  ];

  for (const url of urlsToTest) {
    try {
      console.log(`📡 Testing ${url}...`);
      const res = await fetch(url, {
        headers: {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        },
      });

      if (res.ok) {
        const text = await res.text();
        if (text.includes("<rss") || text.includes("<feed")) {
          console.log(`✅ SUCCESS! Found an active feed at: ${url}`);
          // Print the first 200 characters to verify
          console.log(text.substring(0, 200));
          return;
        }
      }
      console.log(`❌ No XML feed found (Status: ${res.status})`);
    } catch (e) {
      console.log(`❌ Request failed for ${url}`);
    }
  }
}

checkFeed();
