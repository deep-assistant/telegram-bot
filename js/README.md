# Deep Assistant Telegram Bot (JavaScript)

This folder contains the **JavaScript** implementation of the Deep-Assistant Telegram bot. It is designed to be run with **[Bun](https://bun.sh)** only – no `npm`, `yarn`, or `pnpm` required.

---

## 1. Install Bun

If you don’t have Bun yet, install it globally:

```bash
curl -fsSL https://bun.sh/install | bash
# or on macOS with Homebrew
brew install bun
```

Verify that it works:

```bash
bun --version
```

---

## 2. Prepare configuration

1. Copy the example configuration file and edit it with your own credentials:

   ```bash
   cd js
   cp config.example.js config.js
   ```

2. Open `config.js` in your editor and fill in at least:

   * `TOKEN` – Telegram bot token from **@BotFather**
   * `ADMIN_TOKEN` – Admin token for <https://api.deep-foundation.tech> (optional unless you use API features)
   * Any other keys you plan to use (payments, DeepInfra, etc.)

3. Leave `IS_DEV: true` while developing locally. Switch it to `false` for production-like analytics routing.

---

## 3. Install dependencies (with Bun)

Bun reads the `import` statements in the source code and will automatically infer the needed packages. Run:

```bash
bun install
```

This creates/updates `bun.lockb` and a minimal `package.json` when necessary.

> **Tip**   If you add a new library later, simply execute `bun add <package>`.

---

## 4. Run the bot

### Development (long-polling)

```bash
bun run index.js    # or simply `bun index.js`
```

The bot will start in long-polling mode (default when `IS_DEV` is `true`). Check your terminal for the "Starting bot…" log.

### Production (webhook)

1. Set `WEBHOOK_ENABLED: true` and configure `WEBHOOK_URL`, `WEBHOOK_PATH`, `WEBHOOK_HOST`, `WEBHOOK_PORT` in `config.js`.
2. Ensure your server is reachable from the internet (HTTPS is required by Telegram).
3. Start the bot just like in development:

   ```bash
   bun run index.js
   ```

The dispatcher will automatically register/unregister the webhook on startup/shutdown.

---

## 5. Common Bun commands

| Task                        | Command                      |
| --------------------------- | ---------------------------- |
| Install deps                | `bun install`               |
| Add a new dependency        | `bun add <pkg>`             |
| Run the bot                 | `bun run index.js`          |
| Run a single file           | `bun <file>.js`             |
| Update all deps             | `bun update`                |

---

## 6. Q & A

**Q:** _Can I still use `npm`?_

**A:** You could, but this repo is optimized for Bun’s speed and simplicity. Mixing package managers can break the lock-file – stick with Bun.

**Q:** _The bot crashes on missing package X._

**A:** Run `bun add <package>` and try again. Bun only installs what it detects from current imports.

**Q:** _How do I run tests?_ (none yet)

**A:** Coming soon! Feel free to contribute.

---

Happy hacking! ✨ 