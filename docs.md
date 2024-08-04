# API Documentation `Deep.GPT`

## Getting the API key

The key must be obtained in the bot https://t.me/DeepGPTBot , call the `/api` command

<img src="./attachments/doc_image.jpeg" width="400"/>

## Using the API in `JavaScript`

### Installation

```commandline
npm install openai
```

### Usage

```js
import OpenAI from 'openai';

const client = new OpenAI({
  // You can get a token in the bot https://t.me/DeepGPTBot calling the `/api` command
  apiKey: "YOUR KEY", 
  baseURL: "https://api.deep-foundation.tech/v1/"
});

async function main() {
  const chatCompletion = await openai.chat.completions.create({
    messages: [{ role: 'user', content: 'Say this is a test' }],
    model: 'gpt-3.5-turbo',
  });
  
  console.log(chatCompletion.choices[0].delta.content);
}

main();
```

### Streaming responses

```js
import OpenAI from 'openai';

const client = new OpenAI();

async function main() {
  const stream = await openai.chat.completions.create({
    model: 'gpt-3.5-turbo',
    messages: [{ role: 'user', content: 'Say this is a test' }],
    stream: true,
  });
  
  let result = "";
  
  for await (const chunk of stream) {
    result += chunk.choices[0]?.delta?.content || '';
    console.log(result);
  }
}

main();
```

## Using the API in `Python`

### Installation

```commandline
pip install openai
```

### Usage

```python
from openai import OpenAI

openai = OpenAI(
    # You can get a token in the bot https://t.me/DeepGPTBot calling the `/api` command
    api_key="YOUR KEY",
    base_url="https://api.deep-foundation.tech/v1/",
)

chat_completion = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": 'Say this is a test'}],
)

print(chat_completion.choices[0].message.content)
```

### Streaming responses


```python
from openai import OpenAI

openai = OpenAI(
    # You can get a token in the bot https://t.me/DeepGPTBot calling the `/api` command
    api_key="YOUR KEY",
    base_url="https://api.deep-foundation.tech/v1/",
)

stream = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": 'Say this is a test'}],
    stream=True
)

for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="")

```

### List of all available models:
1000 energy = 0.8 RUB = 0,009 USD

- `gpt-4o`: 1000 tokens = 1000 energy
- `gpt-4o-mini`: 1000 tokens = 70 energy
- `gpt-3.5-turbo`: 1000 tokens = 70 energy
- `meta-llama/Meta-Llama-3.1-405B`: 1000  tokens = 800 energy
- `meta-llama/Meta-Llama-3.1-70B`: 1000  tokens = 285 energy
- `meta-llama/Meta-Llama-3-70B-Instruct`: 1000  tokens = 285 energy
- `meta-llama/Meta-Llama-3.1-8B`: 1000 tokens = 20 energy
