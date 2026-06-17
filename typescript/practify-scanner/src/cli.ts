#!/usr/bin/env node
/**
 * practify-scanner CLI
 *
 * Usage:
 *   practify-scanner check <path>
 *   practify-scanner report <path>
 */

import { scanFile, scanDirectory, summarize, PATTERN_SEVERITY } from "./scanner";
import * as fs from "fs";
import * as path from "path";

const args = process.argv.slice(2);
const command = args[0];
const target = args[1];

if (!command || !target) {
  console.log("practify-scanner — Defensive code pattern scanner");
  console.log("");
  console.log("Usage:");
  console.log("  practify-scanner check <path>     Scan for defensive patterns");
  console.log("  practify-scanner report <path>    Generate health report");
  process.exit(0);
}

const targetPath = path.resolve(target);

function main() {
  if (!fs.existsSync(targetPath)) {
    console.error(`ERROR: path not found — ${targetPath}`);
    process.exit(1);
  }

  const isFile = fs.statSync(targetPath).isFile();
  const results = isFile
    ? new Map([[targetPath, scanFile(targetPath)]])
    : scanDirectory(targetPath);

  let totalPatterns = 0;
  for (const [filepath, patterns] of results) {
    if (patterns.length === 0) continue;
    console.log(`\n${"=".repeat(70)}`);
    console.log(`FILE: ${filepath}`);
    console.log(`${"=".repeat(70)}`);

    for (const p of patterns) {
      const sev = PATTERN_SEVERITY[p.patternType].toUpperCase();
      const fnInfo = p.functionName ? ` (in ${p.functionName})` : "";

      console.log(`\n[${sev}] ${p.patternType}${fnInfo}`);
      console.log(`  at ${p.filePath}:${p.lineNumber}`);
      console.log(`  code: ${p.codeSnippet}`);
      console.log(`  suggestion: ${p.suggestion}`);
      totalPatterns++;
    }
  }

  console.log(`\n${"-".repeat(70)}`);
  console.log(
    `Total: ${totalPatterns} defensive patterns (across ${results.size} files)`,
  );

  const allPatterns: any[] = [];
  for (const patterns of results.values()) {
    allPatterns.push(...patterns);
  }
  const summary = summarize(allPatterns);
  console.log(
    `By severity: ERR=${summary.bySeverity["error"]} ` +
      `WARN=${summary.bySeverity["warning"]} ` +
      `INFO=${summary.bySeverity["info"]}`,
  );

  if (summary.bySeverity["error"] > 0) {
    process.exit(1);
  }
}

main();
