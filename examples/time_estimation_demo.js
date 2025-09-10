import { timeEstimationService } from '../js/src/services/index.js';

/**
 * Demonstration of the Time Estimation Feature
 * 
 * This script shows how the time estimation feature works:
 * 1. Records response times for simulated bot interactions
 * 2. Shows how statistics are calculated and stored
 * 3. Demonstrates the user-facing estimation messages
 */

async function simulateBotUsage(userId, responseTimes) {
  console.log(`👤 Simulating bot usage for user ${userId}...`);
  
  for (let i = 0; i < responseTimes.length; i++) {
    const responseTime = responseTimes[i];
    console.log(`   📝 Recording response time #${i + 1}: ${responseTime}ms`);
    await timeEstimationService.recordResponseTime(userId, responseTime);
    
    // Show current statistics after each response
    const stats = await timeEstimationService.getTimeStatistics(userId);
    console.log(`   📊 Current stats: avg=${stats.average?.toFixed(0)}ms, min=${stats.min}ms, max=${stats.max}ms, count=${stats.requestCount}`);
  }
}

async function demonstrateTimeFormatting() {
  console.log('\n🕒 Time Formatting Examples:');
  const times = [
    250,      // milliseconds
    1500,     // 1.5 seconds
    45000,    // 45 seconds
    90000,    // 1.5 minutes
    3600000,  // 1 hour
    7200000   // 2 hours
  ];
  
  times.forEach(time => {
    const formatted = timeEstimationService.formatTime(time);
    console.log(`   ${time}ms → ${formatted}`);
  });
}

async function showUserExperience(userId) {
  console.log(`\n💬 User Experience for ${userId}:`);
  
  // Show what the user would see when using /time command
  const message = await timeEstimationService.getEstimationMessage(userId);
  console.log('   When user types /time, they see:');
  console.log('   ┌─────────────────────────────────────────┐');
  message.split('\n').forEach(line => {
    console.log(`   │ ${line.padEnd(39)} │`);
  });
  console.log('   └─────────────────────────────────────────┘');
}

async function demonstrateRealWorldScenarios() {
  console.log('\n🌍 Real-World Scenarios:\n');
  
  // Scenario 1: New user
  console.log('📁 Scenario 1: Brand new user');
  const newUser = 'new_user_001';
  await showUserExperience(newUser);
  
  // Scenario 2: Fast responses (simple questions)
  console.log('\n⚡ Scenario 2: User asking simple questions (fast responses)');
  const fastUser = 'fast_user_002';
  const fastResponses = [800, 1200, 950, 1100, 850, 1050]; // 800-1200ms range
  await simulateBotUsage(fastUser, fastResponses);
  await showUserExperience(fastUser);
  
  // Scenario 3: Slow responses (complex questions)
  console.log('\n🐌 Scenario 3: User asking complex questions (slow responses)');
  const slowUser = 'slow_user_003';
  const slowResponses = [5000, 7200, 6800, 8100, 5500, 6300]; // 5-8 second range
  await simulateBotUsage(slowUser, slowResponses);
  await showUserExperience(slowUser);
  
  // Scenario 4: Mixed usage patterns
  console.log('\n🔄 Scenario 4: User with mixed usage patterns');
  const mixedUser = 'mixed_user_004';
  const mixedResponses = [1200, 4500, 800, 6200, 1500, 3200, 900, 7800, 1100, 2800]; // Varied responses
  await simulateBotUsage(mixedUser, mixedResponses);
  await showUserExperience(mixedUser);
}

async function demonstrateEdgeCases() {
  console.log('\n🔬 Edge Cases:\n');
  
  // Edge case 1: Very fast responses
  console.log('⚡ Edge Case 1: Very fast responses (< 1 second)');
  const veryFastUser = 'very_fast_user';
  const veryFastResponses = [150, 200, 180, 220, 170];
  await simulateBotUsage(veryFastUser, veryFastResponses);
  await showUserExperience(veryFastUser);
  
  // Edge case 2: Very slow responses
  console.log('\n🕐 Edge Case 2: Very slow responses (> 1 minute)');
  const verySlowUser = 'very_slow_user';
  const verySlowResponses = [75000, 90000, 120000, 85000]; // 1.25-2 minutes
  await simulateBotUsage(verySlowUser, verySlowResponses);
  await showUserExperience(verySlowUser);
  
  // Edge case 3: Single response
  console.log('\n1️⃣ Edge Case 3: User with only one response');
  const singleUser = 'single_response_user';
  await timeEstimationService.recordResponseTime(singleUser, 2500);
  await showUserExperience(singleUser);
}

async function main() {
  console.log('🎯 Time Estimation Feature Demonstration\n');
  console.log('This demo shows how the automatic time estimation works in the Telegram bot.\n');
  
  await demonstrateTimeFormatting();
  await demonstrateRealWorldScenarios();
  await demonstrateEdgeCases();
  
  console.log('\n✨ Feature Summary:');
  console.log('• ⏱️  Automatically tracks response times for each user');
  console.log('• 📊 Calculates average, minimum, and maximum response times');
  console.log('• 💾 Stores up to 100 recent response times per user');
  console.log('• 📱 Provides user-friendly time formatting (ms, s, min, h)');
  console.log('• 🤖 Available via /time command or ⏱️ Время ответа button');
  console.log('• 🔒 Each user sees only their own statistics');
  console.log('• 🚀 Helps users understand typical bot response times');
  
  console.log('\n🎉 Time Estimation Feature Demo Complete!');
}

// Run the demonstration
main().catch(console.error);