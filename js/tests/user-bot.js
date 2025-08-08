import fs from 'fs';

// Load dynamic import helper from CDN like the original
const { use } = eval(await fetch('https://unpkg.com/use-m/use.js').then(u => u.text()));

export async function initTelegramConnection() {
  const telegram = await use('telegram');
  const input = await use('readline-sync');

  process.on('unhandledRejection', err => {
    console.error('Unhandled Rejection:', err);
    process.exit(1);
  });

  const { TelegramClient, Api } = telegram;
  const { StringSession } = telegram.sessions;

  const apiId = process.env.TELEGRAM_API_ID || input.question('Enter your Telegram API ID: ');
  const apiHash = process.env.TELEGRAM_API_HASH || input.question('Enter your Telegram API Hash: ');

  const sessionFile = './.telegram_session';
  const fileExists = fs.existsSync(sessionFile);
  let storedSession = '';
  if (fileExists) {
    storedSession = (await fs.promises.readFile(sessionFile, 'utf8')).trim();
  }

  const stringSession = new StringSession(storedSession);
  const client = new TelegramClient(stringSession, parseInt(apiId, 10), apiHash, { connectionRetries: 5 });

  await client.start({
    phoneNumber: async () => process.env.TELEGRAM_PHONE || input.question('Enter your phone number: '),
    password: async () => input.question('Enter your 2FA password (if any): '),
    phoneCode: async () => input.question('Enter the code you received: '),
    onError: err => console.error(err),
  });

  if (!fileExists) {
    await fs.promises.writeFile(sessionFile, client.session.save(), 'utf8');
  }

  return { client, Api };
}

export async function usingTelegram(fn) {
  const { client, Api } = await initTelegramConnection();
  try {
    return await fn({ client, Api });
  } finally {
    await client.disconnect();
  }
}

export async function setupOrCheckSession() {
  const sessionFile = './.telegram_session';
  const fileExists = fs.existsSync(sessionFile);
  
  if (fileExists) {
    console.log('✅ Session file exists, checking connection...');
    try {
      await usingTelegram(async ({ client }) => {
        const me = await client.getMe();
        console.log(`✅ Connected successfully as ${me.firstName} ${me.lastName || ''}`);
      });
      return true;
    } catch (error) {
      console.log('❌ Session invalid, creating new one...');
      fs.unlinkSync(sessionFile);
      return await setupOrCheckSession();
    }
  } else {
    console.log('📱 No session found, creating new session...');
    try {
      await usingTelegram(async ({ client }) => {
        const me = await client.getMe();
        console.log(`✅ New session created for ${me.firstName} ${me.lastName || ''}`);
      });
      return true;
    } catch (error) {
      console.error('❌ Failed to create session:', error.message);
      return false;
    }
  }
}