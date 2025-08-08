import { ALL_COMMANDS } from './commands.js';

// Checks if prompt is empty or just a command
export function isEmptyPrompt(prompt) {
  const stripped = prompt.trim();
  // Check if prompt is exactly a bot command
  if (ALL_COMMANDS.includes(stripped)) return true;
  // Check single slash commands like /start
  if (/^\/[a-zA-Z]+$/.test(stripped)) return true;
  // Check internal commands of form 1:midjourney:...
  if (/^1:(midjourney|dalle|flux|sd|suno):.+$/.test(stripped)) return true;
  // Check if no alphanumeric characters
  if (!/[A-Za-z0-9]/.test(stripped)) return true;
  return false;
}
