#!/usr/bin/env node
/**
 * Test script for filename extraction functionality in JavaScript.
 * Tests the extractHumanReadableFilename function with various URL types.
 */

import { extractHumanReadableFilename } from '../js/src/services/utils.js';

function testDiscordUrl() {
  // Test with the Discord CDN URL from the GitHub issue
  const url = "https://cdn.discordapp.com/attachments/1334433356263194676/1335313374656860181/deborah_ua1077041_anime_girl_2e86d324-0275-412f-9413-b5298dc1593f.png?ex=679fb6fd&is=679e657d&hm=c58ae42143406364740aea7627649988d709ec47c86eacf9340a366a874bdd76&";
  
  const result = extractHumanReadableFilename(url);
  const expected = "deborah_anime_girl.png";
  
  console.log("Discord URL Test:");
  console.log(`Input URL: ${url}`);
  console.log(`Expected: ${expected}`);
  console.log(`Got: ${result}`);
  console.log(`Pass: ${result === expected}`);
  console.log();
  
  return result === expected;
}

function testGenericUrls() {
  // Test with various generic URLs
  const testCases = [
    {
      url: "https://example.com/images/sunset_beach_2023.jpg",
      expected: "sunset_beach_2023.jpg",
      description: "Simple filename"
    },
    {
      url: "https://api.service.com/generate/image123456789abcdef.png",
      expected: "image.png", // Should clean hex sequences
      description: "URL with long hex sequence"
    },
    {
      url: "https://example.com/mountain.jpeg",
      expected: "mountain.jpeg",
      description: "Simple filename with .jpeg extension"
    },
    {
      url: "https://example.com/path/without/extension",
      expected: "extension.png", // Default extension
      description: "URL without file extension"
    },
    {
      url: "https://example.com/",
      expected: "image.png", // Fallback for empty filename
      description: "URL with no filename"
    }
  ];
  
  let allPassed = true;
  
  testCases.forEach((testCase, index) => {
    const result = extractHumanReadableFilename(testCase.url);
    const passed = result === testCase.expected;
    allPassed = allPassed && passed;
    
    console.log(`Test ${index + 1}: ${testCase.description}`);
    console.log(`Input: ${testCase.url}`);
    console.log(`Expected: ${testCase.expected}`);
    console.log(`Got: ${result}`);
    console.log(`Pass: ${passed}`);
    console.log();
  });
  
  return allPassed;
}

function testDiscordVariations() {
  // Test with various Discord URL patterns
  const testCases = [
    {
      url: "https://cdn.discordapp.com/attachments/123/456/anime_girl_art.png",
      expected: "anime_girl_art.png",
      description: "Simple Discord filename"
    },
    {
      url: "https://cdn.discordapp.com/attachments/123/456/user123_portrait_abcd1234-5678-9012-3456-789012345678.jpg",
      expected: "portrait.jpg",
      description: "Discord filename with user ID and UUID"
    },
    {
      url: "https://media.discordapp.net/attachments/123/456/sunset_photo_final.png?width=800&height=600",
      expected: "sunset_photo_final.png",
      description: "Discord media URL with query parameters"
    }
  ];
  
  let allPassed = true;
  
  testCases.forEach((testCase, index) => {
    const result = extractHumanReadableFilename(testCase.url);
    const passed = result === testCase.expected;
    allPassed = allPassed && passed;
    
    console.log(`Discord Variation ${index + 1}: ${testCase.description}`);
    console.log(`Input: ${testCase.url}`);
    console.log(`Expected: ${testCase.expected}`);
    console.log(`Got: ${result}`);
    console.log(`Pass: ${passed}`);
    console.log();
  });
  
  return allPassed;
}

function main() {
  console.log("Testing filename extraction functionality (JavaScript)");
  console.log("=" .repeat(50));
  console.log();
  
  // Test the main Discord URL from the issue
  const discordTest = testDiscordUrl();
  
  // Test generic URLs
  console.log("Generic URL Tests:");
  console.log("-".repeat(20));
  const genericTest = testGenericUrls();
  
  // Test Discord variations
  console.log("Discord Variation Tests:");
  console.log("-".repeat(25));
  const discordVariationsTest = testDiscordVariations();
  
  // Summary
  console.log("Test Summary:");
  console.log("-".repeat(15));
  console.log(`Discord URL Test: ${discordTest ? 'PASS' : 'FAIL'}`);
  console.log(`Generic URL Tests: ${genericTest ? 'PASS' : 'FAIL'}`);
  console.log(`Discord Variations: ${discordVariationsTest ? 'PASS' : 'FAIL'}`);
  
  const allTestsPassed = discordTest && genericTest && discordVariationsTest;
  console.log(`Overall Result: ${allTestsPassed ? 'ALL TESTS PASSED' : 'SOME TESTS FAILED'}`);
  
  return allTestsPassed ? 0 : 1;
}

// Run the tests
process.exit(main());