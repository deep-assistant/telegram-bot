import { timeEstimationService } from '../src/services/index.js';

// Simple test framework
class TestRunner {
  constructor() {
    this.tests = [];
    this.passed = 0;
    this.failed = 0;
  }

  async test(name, testFn) {
    console.log(`\n🧪 Running test: ${name}`);
    try {
      await testFn();
      console.log(`✅ PASSED: ${name}`);
      this.passed++;
    } catch (error) {
      console.log(`❌ FAILED: ${name}`);
      console.log(`   Error: ${error.message}`);
      this.failed++;
    }
  }

  assertEqual(actual, expected, message = '') {
    if (actual !== expected) {
      throw new Error(`${message}\n   Expected: ${expected}\n   Actual: ${actual}`);
    }
  }

  assertTrue(condition, message = '') {
    if (!condition) {
      throw new Error(`${message}\n   Expected: true\n   Actual: false`);
    }
  }

  assertNotNull(value, message = '') {
    if (value === null || value === undefined) {
      throw new Error(`${message}\n   Expected: not null/undefined\n   Actual: ${value}`);
    }
  }

  async run() {
    console.log('\n🚀 Starting Time Estimation Service Tests\n');
    await this.runTests();
    console.log('\n📊 Test Results:');
    console.log(`✅ Passed: ${this.passed}`);
    console.log(`❌ Failed: ${this.failed}`);
    console.log(`📈 Total: ${this.passed + this.failed}`);
    
    if (this.failed === 0) {
      console.log('\n🎉 All tests passed!');
    } else {
      console.log('\n💥 Some tests failed!');
      process.exit(1);
    }
  }

  async runTests() {
    const testUserId = 'test_user_123';
    
    // Test 1: Initial state - no data
    await this.test('Should return no data for new user', async () => {
      const stats = await timeEstimationService.getTimeStatistics(testUserId);
      this.assertEqual(stats.average, null);
      this.assertEqual(stats.min, null);
      this.assertEqual(stats.max, null);
      this.assertEqual(stats.requestCount, 0);
    });

    // Test 2: Record first response time
    await this.test('Should record first response time', async () => {
      await timeEstimationService.recordResponseTime(testUserId, 1500);
      const stats = await timeEstimationService.getTimeStatistics(testUserId);
      
      this.assertEqual(stats.average, 1500);
      this.assertEqual(stats.min, 1500);
      this.assertEqual(stats.max, 1500);
      this.assertEqual(stats.requestCount, 1);
    });

    // Test 3: Record multiple response times
    await this.test('Should handle multiple response times correctly', async () => {
      await timeEstimationService.recordResponseTime(testUserId, 2000);
      await timeEstimationService.recordResponseTime(testUserId, 1000);
      await timeEstimationService.recordResponseTime(testUserId, 3000);
      
      const stats = await timeEstimationService.getTimeStatistics(testUserId);
      
      // Average should be (1500 + 2000 + 1000 + 3000) / 4 = 1875
      this.assertEqual(stats.average, 1875);
      this.assertEqual(stats.min, 1000);
      this.assertEqual(stats.max, 3000);
      this.assertEqual(stats.requestCount, 4);
    });

    // Test 4: Format time function
    await this.test('Should format time correctly', () => {
      this.assertEqual(timeEstimationService.formatTime(500), '500мс');
      this.assertEqual(timeEstimationService.formatTime(1500), '1.5с');
      this.assertEqual(timeEstimationService.formatTime(65000), '1.1мин');
      this.assertEqual(timeEstimationService.formatTime(3700000), '1.0ч');
    });

    // Test 5: Estimation message
    await this.test('Should generate correct estimation message', async () => {
      const message = await timeEstimationService.getEstimationMessage(testUserId);
      this.assertTrue(message.includes('Статистика времени ответа'));
      this.assertTrue(message.includes('1.9с')); // Average 1875ms = 1.9s
      this.assertTrue(message.includes('1.0с')); // Min 1000ms = 1.0s
      this.assertTrue(message.includes('3.0с')); // Max 3000ms = 3.0s
      this.assertTrue(message.includes('4')); // Request count
    });

    // Test 6: Invalid response times
    await this.test('Should handle invalid response times', async () => {
      const statsBefore = await timeEstimationService.getTimeStatistics(testUserId);
      
      // These should not be recorded
      await timeEstimationService.recordResponseTime(testUserId, -1);
      await timeEstimationService.recordResponseTime(testUserId, 0);
      await timeEstimationService.recordResponseTime(testUserId, null);
      await timeEstimationService.recordResponseTime(testUserId, undefined);
      await timeEstimationService.recordResponseTime(testUserId, 'invalid');
      
      const statsAfter = await timeEstimationService.getTimeStatistics(testUserId);
      
      // Statistics should remain the same
      this.assertEqual(statsAfter.average, statsBefore.average);
      this.assertEqual(statsAfter.min, statsBefore.min);
      this.assertEqual(statsAfter.max, statsBefore.max);
      this.assertEqual(statsAfter.requestCount, statsBefore.requestCount);
    });

    // Test 7: New user estimation message
    await this.test('Should handle new user with no data', async () => {
      const newUserId = 'new_user_456';
      const message = await timeEstimationService.getEstimationMessage(newUserId);
      this.assertEqual(message, '⏱️ Еще нет данных для оценки времени ответа');
    });

    // Test 8: Very large response time collection (test maxStoredTimes limit)
    await this.test('Should limit stored response times', async () => {
      const testUserId2 = 'test_user_limit';
      
      // Add more than maxStoredTimes (100) response times
      for (let i = 0; i < 105; i++) {
        await timeEstimationService.recordResponseTime(testUserId2, 1000 + i);
      }
      
      const responseTimes = await timeEstimationService.getResponseTimes(testUserId2);
      this.assertTrue(responseTimes.length <= 100, `Response times length should be <= 100, got ${responseTimes.length}`);
      
      // The oldest times should be removed, so we should have times from 1005 to 1104
      this.assertEqual(responseTimes[0], 1005); // First should be 1005 (original 1000 + 5, since first 5 were removed)
      this.assertEqual(responseTimes[responseTimes.length - 1], 1104); // Last should be 1104
    });
  }
}

// Run the tests
const runner = new TestRunner();
runner.run().catch(console.error);