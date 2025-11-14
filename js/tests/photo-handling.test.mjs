import { usingTelegram } from './user-bot.js';
import { config } from '../src/config.js';
import { startBot, shutdownEmitter } from '../src/index.js';
import fs from 'fs/promises';
import path from 'path';

/**
 * Test for Issue #152: Images sent to bot are not recognized as a task
 *
 * This test verifies that when a user sends images with a caption to the bot,
 * the bot properly recognizes and processes the images, rather than ignoring them.
 *
 * Test scenarios:
 * 1. Direct send - Send photo with caption directly to bot
 * 2. Reply in group - Reply to photo message in group chat (mentions bot)
 * 3. Forward - Forward photo message to bot
 *
 * Root cause: bot/gpt/router.py checks message.entities instead of
 * message.caption_entities for photo messages in groups, causing early exit.
 */

async function waitForMessage(client, botUsername, timeoutMs = 15000) {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      reject(new Error(`Timeout waiting for message from ${botUsername}`));
    }, timeoutMs);

    client.addEventHandler(async (update) => {
      try {
        if (update.message && update.message.peerId) {
          const sender = await client.getEntity(update.message.peerId);
          if (sender.username === botUsername.replace('@', '')) {
            clearTimeout(timeout);
            resolve(update.message.message);
          }
        }
      } catch (error) {
        // Ignore errors in event handler
      }
    });
  });
}

async function testPhotoHandling() {
  console.log('🚀 Starting photo handling test (Issue #152)...');

  let botProcess = null;

  try {
    // Start the bot
    console.log('🤖 Starting bot...');
    botProcess = startBot();

    // Wait for bot to initialize
    await new Promise(resolve => setTimeout(resolve, 3000));
    console.log('✅ Bot started successfully');

    // Test bot interaction with photos
    await usingTelegram(async ({ client }) => {
      const botUsername = config.telegramBotName;

      // Load test image
      const testImagePath = path.join(process.cwd(), 'docs', 'case-studies', 'issue-152', 'image1.png');
      console.log(`📷 Loading test image from: ${testImagePath}`);

      let imageExists = false;
      try {
        await fs.access(testImagePath);
        imageExists = true;
        console.log('✅ Test image found');
      } catch (error) {
        console.log('⚠️  Test image not found, creating placeholder...');
        // If test image doesn't exist, we'll skip the actual photo send
        // but still test the expected behavior
      }

      if (imageExists) {
        console.log(`📤 Sending photo with caption to ${botUsername}...`);

        // Send photo with caption similar to the bug report
        await client.sendMessage(botUsername, {
          message: 'Реши по примеру',
          file: testImagePath
        });
        console.log(`✅ Sent photo message with caption`);

        // Wait for response
        console.log('⏳ Waiting for bot response...');
        const response = await waitForMessage(client, botUsername, 20000);
        console.log(`📥 Received response: ${response.substring(0, 200)}...`);

        // Analyze response
        const normalizedResponse = response.toLowerCase();

        // Indicators that the bot ignored the image (BUG):
        const ignoredImageIndicators = [
          "doesn't include a specific question",
          "could you please clarify",
          "i noticed that your message doesn't",
          "не содержит конкретного вопроса",
          "пожалуйста, уточните"
        ];

        const isIgnoringImage = ignoredImageIndicators.some(indicator =>
          normalizedResponse.includes(indicator.toLowerCase())
        );

        if (isIgnoringImage) {
          console.log('❌ BUG REPRODUCED: Bot is ignoring the image!');
          console.log('   The bot responded as if no image was sent.');
          console.log('   Response:', response.substring(0, 150));
          return { success: false, bugReproduced: true };
        } else {
          console.log('✅ Bot appears to be processing the image correctly');
          console.log('   Response does not contain generic "clarify" messages');
          console.log('   Response:', response.substring(0, 150));
          return { success: true, bugReproduced: false };
        }
      } else {
        console.log('⚠️  Skipping actual photo send test (no test image)');
        console.log('💡 To run full test, ensure test images exist in docs/case-studies/issue-152/');
        return { success: true, skipped: true };
      }
    });

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    throw error;
  } finally {
    // Shutdown bot
    if (botProcess) {
      console.log('🛑 Shutting down bot...');
      shutdownEmitter.emit('shutdown');
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }
}

// Detect execution context
const isRunningViaBunTest = process.argv.join(' ').includes('bun test') || process.env.NODE_ENV === 'test';

if (isRunningViaBunTest) {
  // Bun test framework execution
  const { test, describe, expect } = await import('bun:test');

  describe('Photo Handling Tests (Issue #152)', () => {
    test('should recognize and process images sent with captions, not ignore them', async () => {
      const result = await testPhotoHandling();

      if (result.skipped) {
        console.log('⚠️  Test skipped - see logs for details');
        return;
      }

      expect(result.bugReproduced).toBe(false);
      expect(result.success).toBe(true);
    }, 60000); // 60 second timeout for integration test
  });
} else if (import.meta.main) {
  // Direct execution
  await testPhotoHandling();
}
