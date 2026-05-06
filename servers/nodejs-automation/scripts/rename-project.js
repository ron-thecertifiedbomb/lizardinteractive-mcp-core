#!/usr/bin/env node

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

// Support __dirname in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function updateJsonFile(filePath, replacer) {
  if (fs.existsSync(filePath)) {
    const content = fs.readFileSync(filePath, "utf8");
    const json = JSON.parse(content);
    replacer(json);
    fs.writeFileSync(filePath, JSON.stringify(json, null, 2));
  }
}

function replaceInFile(filePath, oldName, newName) {
  if (fs.existsSync(filePath)) {
    const content = fs.readFileSync(filePath, "utf8");
    const updated = content.replace(new RegExp(oldName, "g"), newName);
    fs.writeFileSync(filePath, updated);
  }
}

function renameProject(newName) {
  const rootDir = path.resolve(__dirname, ".."); // Adjusted to work when script is in "scripts/" folder
  const packageJsonPath = path.join(rootDir, "package.json");
  const appJsonPath = path.join(rootDir, "app.json");
  const iosPath = path.join(rootDir, "ios");
  const androidPath = path.join(rootDir, "android");

  if (!fs.existsSync(packageJsonPath)) {
    console.error("❌ Could not find package.json in project root.");
    process.exit(1);
  }

  // Read old project name from package.json
  const pkg = JSON.parse(fs.readFileSync(packageJsonPath, "utf8"));
  const oldName = pkg.name;

  console.log(`🔄 Renaming project from "${oldName}" to "${newName}"...`);

  // Update package.json
  updateJsonFile(packageJsonPath, (json) => {
    json.name = newName;
  });

  // Update app.json if exists
  if (fs.existsSync(appJsonPath)) {
    updateJsonFile(appJsonPath, (json) => {
      if (json.expo) {
        if (json.expo.name) json.expo.name = newName;
        if (json.expo.slug) json.expo.slug = newName;
        if (json.expo.displayName) json.expo.displayName = newName;
      }
    });
  }
  // iOS: Rename .xcodeproj and .xcworkspace, update project.pbxproj and Info.plist
  if (fs.existsSync(iosPath)) {
    const oldProj = path.join(iosPath, `${oldName}.xcodeproj`);
    const newProj = path.join(iosPath, `${newName}.xcodeproj`);
    if (fs.existsSync(oldProj)) fs.renameSync(oldProj, newProj);

    const oldWsp = path.join(iosPath, `${oldName}.xcworkspace`);
    const newWsp = path.join(iosPath, `${newName}.xcworkspace`);
    if (fs.existsSync(oldWsp)) fs.renameSync(oldWsp, newWsp);

    // Update project.pbxproj
    const pbxproj = path.join(newProj, "project.pbxproj");
    replaceInFile(pbxproj, oldName, newName);

    // Update Info.plist
    const infoPlist = path.join(iosPath, newName, "Info.plist");
    replaceInFile(infoPlist, oldName, newName);
  }

  // Android: Update settings.gradle, app/build.gradle, and AndroidManifest.xml
  if (fs.existsSync(androidPath)) {
    const settingsGradle = path.join(androidPath, "settings.gradle");
    replaceInFile(settingsGradle, oldName, newName);

    const appBuildGradle = path.join(androidPath, "app", "build.gradle");
    replaceInFile(appBuildGradle, oldName, newName);

    const manifest = path.join(
      androidPath,
      "app",
      "src",
      "main",
      "AndroidManifest.xml"
    );
    replaceInFile(manifest, oldName, newName);
  }

  console.log(`✅ Project renamed from "${oldName}" to "${newName}".`);
}

// Run the script
const newName = process.argv[2];
if (!newName) {
  console.error("❌ Please provide a new project name");
  process.exit(1);
}
renameProject(newName);
