import { include } from './utils.js';
import { stateService, StateTypes } from '../services/index.js';

export class CompositeFilters {
  constructor(filters) {
    this.filters = filters;
  }

  async call(message) {
    for (const Filter of this.filters) {
      // Assume Filter has a call method
      const result = await Filter.call(message);
      if (!result) return false;
    }
    return true;
  }
}

class _TextCommand {
  constructor(textCommand) {
    this.textCommands = Array.isArray(textCommand) ? textCommand : [textCommand];
  }

  async call(message) {
    if (message.forward_date || message.forward_from) return false;
    if (message.reply_to_message) return false;
    if (!message.text) return false;
    return this.textCommands.some(cmd => message.text.trim().startsWith(cmd));
  }
}

export function TextCommand(textCommand) {
  return new _TextCommand(textCommand);
}

export class StartWith {
  constructor(textCommand) {
    this.textCommand = textCommand;
  }

  async call(message) {
    if (!message.text) return false;
    return message.text.startsWith(this.textCommand);
  }
}

export class Document {
  async call(message) {
    return message.document != null;
  }
}

export class Photo {
  async call(message) {
    return message.photo != null;
  }
}

export class Video {
  async call(message) {
    return message.video != null;
  }
}

export class Voice {
  async call(message) {
    return message.voice != null;
  }
}

export class Audio {
  async call(message) {
    return message.audio != null;
  }
}

export function StartWithQuery(textCommand) {
  return {
    async call(callbackQuery) {
      return callbackQuery.data.startsWith(textCommand);
    }
  };
}

export class TextCommandQuery {
  constructor(textCommands) {
    this.textCommands = textCommands;
  }

  async call(callbackQuery) {
    return include(this.textCommands, callbackQuery.data);
  }
}

export class StateCommand {
  constructor(state) {
    this.state = state;
  }

  async call(message) {
    // Compare user's current state to desired state
    const current = await stateService.getCurrentState(message.from_user.id);
    return current === this.state;
  }
}
