# API Documentation `Deep.GPT`

## Getting the API key

The key must be obtained in the bot https://t.me/DeepGPTBot , call the `/api` command

<img src="./attachments/doc_image.jpeg" width="400"/>

## Using the API in `JavaScript`

### LLM

### Installation

```commandline
npm install openai
```

### Usage

```js
import OpenAI from 'openai';

const openai = new OpenAI({
  // You can get a token in the bot https://t.me/DeepGPTBot calling the `/api` command
  apiKey: "DEEP_TOKEN", 
  baseURL: "https://api.deep-foundation.tech/v1/"
});

async function main() {
  const chatCompletion = await openai.chat.completions.create({
    messages: [{ role: 'user', content: 'Say this is a test' }],
    model: 'gpt-4o',
  });
  
  console.log(chatCompletion.choices[0].message.content);
}

main();
```

### Streaming responses

```js
import OpenAI from 'openai';

const openai = new OpenAI({
  // You can get a token in the bot https://t.me/DeepGPTBot calling the `/api` command
  apiKey: "DEEP_TOKEN", 
  baseURL: "https://api.deep-foundation.tech/v1/"
});

async function main() {
  const stream = await openai.chat.completions.create({
    model: 'gpt-4o',
    messages: [{ role: 'user', content: 'Say this is a test' }],
    stream: true,
  });
  
  let result = "";
  
  for await (const chunk of stream) {
    result += chunk.choices[0]?.message?.content || '';
    console.log(result);
  }
}

main();
```

### Whisper

```js

const formData = new FormData();
formData.append("file", file.buffer, file.originalname);
formData.append("model", "whisper-1");
formData.append("language", "RU");

const response = await fetch("https://api.deep-foundation.tech/v1/audio/transcriptions", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${DEEP_TOKEN}`,
    ...formData.getHeaders(),
  },
  body: formData,
});

const responseData = await response.json();

console.log(responseData) // {"text": "hello"}

```

### TTS

```js
import fetch from 'node-fetch';
import { writeFileSync } from 'fs';

const API_URL = 'https://api.deep-foundation.tech/v1/audio/speech';
const TOKEN = 'DEEP_TOKEN'; // Замените на ваш токен

const requestBody = {
  model: 'tts-1',
  input: 'Hello, World',
  voice: 'alloy'
};

const requestOptions = {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${TOKEN}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(requestBody)
};

async function generateSpeech() {
  try {
    const response = await fetch(API_URL, requestOptions);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`Error HTTP: ${response.status} ${response.statusText} - ${JSON.stringify(errorData)}`);
    }

    const buffer = await response.buffer();

    writeFileSync('speech.mp3', buffer);

    const tokenCost = response.headers.get('X-Token-Cost');
    if (tokenCost) {
      console.log(`[TTS Client] Enegry: ${tokenCost}`);
    }

  } catch (error) {
    console.error('[TTS Client] Error:', error.message);
  }
}

generateSpeech();
```

## Using the API in `Python`

### Installation

```commandline
pip install openai
```

### Usage

### LLM

```python
from openai import OpenAI

openai = OpenAI(
    # You can get a token in the bot https://t.me/DeepGPTBot calling the `/api` command
    api_key="DEEP_TOKEN",
    base_url="https://api.deep-foundation.tech/v1/",
)

chat_completion = openai.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": 'Say this is a test'}],
)

print(chat_completion.choices[0].message.content)
```

### Streaming responses


```python
from openai import OpenAI

openai = OpenAI(
    # You can get a token in the bot https://t.me/DeepGPTBot calling the `/api` command
    api_key="DEEP_TOKEN",
    base_url="https://api.deep-foundation.tech/v1/",
)

stream = openai.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": 'Say this is a test'}],
    stream=True
)

for chunk in stream:
    print(chunk.choices[0].message.content or "", end="")

```
### Whisper

```python

import requests

API_KEY = 'DEEP_TOKEN'  
url = "https://api.deep-foundation.tech/v1/audio/transcriptions"

file_buffer = b'...'
file_name = 'your_file_name.mp3' 

files = {'file': (file_name, file_buffer)}
data = {
    'model': 'whisper-1',
    'language': 'RU',
}

headers = { 'Authorization': f'Bearer {YOUR KEY}' }

response = requests.post(url, headers=headers, files=files, data=data)
response_data = response.json()

print(response_data)  # {"text": "hello"}

```

### TTS

```python
import requests
import json

API_URL = 'https://api.deep-foundation.tech/v1/audio/speech'
TOKEN = 'DEEP_TOKEN'  

request_body = {
    'model': 'tts-1',
    'input': 'Hello, World',
    'voice': 'alloy'
}

headers = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}

def generate_speech():
    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(request_body), timeout=30)

        if response.status_code != 200:
            error_data = response.json()
            raise Exception(f'Error HTTP: {response.status_code} {response.reason} - {error_data}')

        with open('speech.mp3', 'wb') as f:
            f.write(response.content)

        token_cost = response.headers.get('X-Token-Cost')
        if token_cost:
            print(f'[TTS Client] Energy: {token_cost}')

    except Exception as e:
        print('[TTS Client] Error:', str(e))

if __name__ == '__main__':
    generate_speech()
```

### List of All Available Models

**1000⚡️ = 0.8 RUB = 0.009 USD**

| Model                   | Price per 1000 tokens (⚡️) |
|-------------------------|-----------------------------|
| `claude-3-opus`         | 6000 ⚡️                      |
| `claude-3-5-sonnet`     | 1000 ⚡️                      |
| `claude-3-5-haiku`      | 100 ⚡️                       |
| `o1-preview`            | 5000 ⚡️                      |
| `o1-mini`               | 800 ⚡️                       |
| `GPT-4o-unofficial`     | 1100 ⚡️                      |
| `GPT-4o`                | 1000 ⚡️                      |
| `GPT-Auto`              | 150 ⚡️                       |
| `GPT-4o-mini`           | 70 ⚡️                        |
| `GPT-3.5-turbo`         | 50 ⚡️                        |
| `Llama3.1-405B`         | 500 ⚡️                       |
| `Llama3.1-70B`          | 250 ⚡️                       |
| `Llama-3.1-8B`          | 20 ⚡️                        |

### Whisper price
- `whisper-1`: 1 minute = 6000⚡️

### TTS price
- 1000 characters = 500⚡️
