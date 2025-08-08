export default class OpenAI {
  constructor(options = {}) {
    this.options = options;
    this.chat = {
      completions: {
        create: async ({ model, messages, max_tokens = 1024, stream = false }) => {
          // Simple echo stub response
          const userContent = messages?.find(m => m.role === 'user')?.content ?? '';
          return {
            choices: [{ message: { content: `Stubbed response for model ${model}. Echo: ${userContent}` } }],
            model: model || 'stub-model',
            usage: { total_tokens: 0 }
          };
        }
      }
    };
  }
}

// Also export named for compatibility
export { OpenAI }; 