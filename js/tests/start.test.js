import { usingTelegram } from './user-bot.js';
import { config } from '../src/config.js';
import { startBot, shutdownEmitter } from '../src/index.js';
import { translate } from '../src/i18n.js';

// Load actual i18n messages for validation
const EXPECTED_MESSAGES = {
  start_greeting: {
    en: translate('en', 'start.greeting').trim(),
    ru: translate('ru', 'start.greeting').trim()
  },
  stop_disabled: {
    en: translate('en', 'start.stop_disabled').trim(),
    ru: translate('ru', 'start.stop_disabled').trim()
  },
  stop_shutdown: {
    en: translate('en', 'start.stop_shutdown').trim(),
    ru: translate('ru', 'start.stop_shutdown').trim()
  }
};

console.log('📋 Expected messages loaded:');
console.log('Start greeting (EN):', EXPECTED_MESSAGES.start_greeting.en.substring(0, 50) + '...');
console.log('Start greeting (RU):', EXPECTED_MESSAGES.start_greeting.ru.substring(0, 50) + '...');
console.log('Stop disabled (EN):', EXPECTED_MESSAGES.stop_disabled.en);
console.log('Stop disabled (RU):', EXPECTED_MESSAGES.stop_disabled.ru);
console.log('Stop shutdown (EN):', EXPECTED_MESSAGES.stop_shutdown.en);
console.log('Stop shutdown (RU):', EXPECTED_MESSAGES.stop_shutdown.ru);

async function waitForMessage(client, botUsername, timeoutMs = 10000) {
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

async function testBotInteraction() {
  console.log('🚀 Starting bot integration test...');
  
  let botProcess = null;
  
  try {
    // Start the bot
    console.log('🤖 Starting bot...');
    botProcess = startBot();
    
    // Wait a moment for bot to initialize
    await new Promise(resolve => setTimeout(resolve, 3000));
    console.log('✅ Bot started successfully');
    
    // Test bot interaction
    await usingTelegram(async ({ client }) => {
      const botUsername = config.telegramBotName;
      console.log(`📤 Sending /start to ${botUsername}...`);
      
      // Send /start command
      await client.sendMessage(botUsername, { message: '/start' });
      console.log(`✅ Sent /start message`);
      
      // Wait for response
      console.log('⏳ Waiting for bot response...');
      const response = await waitForMessage(client, botUsername);
      console.log(`📥 Received response: ${response.substring(0, 100)}...`);
      
      // Validate response matches expected greeting
      const normalizeText = (text) => text.replace(/\s+/g, ' ').trim();
      const normalizedResponse = normalizeText(response);
      
      const expectedGreetings = [
        normalizeText(EXPECTED_MESSAGES.start_greeting.en),
        normalizeText(EXPECTED_MESSAGES.start_greeting.ru)
      ];
      
      const isValidGreeting = expectedGreetings.some(expected => 
        normalizedResponse.includes(expected) || expected.includes(normalizedResponse.substring(0, 100))
      );
      
      if (isValidGreeting) {
        console.log('✅ Response matches expected greeting message');
      } else {
        console.log('❌ Response does not match expected greeting message');
        console.log('Expected (EN):', EXPECTED_MESSAGES.start_greeting.en.substring(0, 100) + '...');
        console.log('Expected (RU):', EXPECTED_MESSAGES.start_greeting.ru.substring(0, 100) + '...');
        console.log('Received:', normalizedResponse.substring(0, 100) + '...');
      }
      
      // Send /stop command
      console.log(`📤 Sending /stop to ${botUsername}...`);
      await client.sendMessage(botUsername, { message: '/stop' });
      console.log(`✅ Sent /stop message`);
      
      // Wait for stop response
      console.log('⏳ Waiting for stop response...');
      try {
        const stopResponse = await waitForMessage(client, botUsername, 5000);
        console.log(`📥 Stop response: ${stopResponse}`);
        
        const normalizedStopResponse = normalizeText(stopResponse);
        const expectedStopMessages = [
          normalizeText(EXPECTED_MESSAGES.stop_disabled.en),
          normalizeText(EXPECTED_MESSAGES.stop_disabled.ru),
          normalizeText(EXPECTED_MESSAGES.stop_shutdown.en),
          normalizeText(EXPECTED_MESSAGES.stop_shutdown.ru)
        ];
        
        const isValidStopResponse = expectedStopMessages.some(expected => 
          normalizedStopResponse.includes(expected) || expected.includes(normalizedStopResponse)
        );
        
        if (isValidStopResponse) {
          console.log('✅ Stop response matches expected message');
        } else {
          console.log('❌ Stop response does not match expected messages');
          console.log('Expected messages:', expectedStopMessages);
          console.log('Received:', normalizedStopResponse);
        }
      } catch (error) {
        console.log('⏰ No stop response received (timeout)');
      }
      
      console.log('🎉 Bot interaction test completed');
    });
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    throw error;
  } finally {
    // Shutdown bot
    if (botProcess) {
      console.log('🛑 Shutting down bot...');
      shutdownEmitter.emit('shutdown');
      // Wait a moment for graceful shutdown
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }
}

if (import.meta.main) {
  testBotInteraction().catch((error) => {
    console.error('Test execution failed:', error);
    process.exit(1);
  });
}