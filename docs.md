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
  apiKey: "YOUR KEY", 
  baseURL: "https://api.deep-foundation.tech/v1/"
});

async function main() {
  const chatCompletion = await openai.chat.completions.create({
    messages: [{ role: 'user', content: 'Say this is a test' }],
    model: 'gpt-3.5-turbo',
  });
  
  console.log(chatCompletion.choices[0].message.content);
}

main();
```

### Streaming responses

```js
import OpenAI from 'openai';

const openai = new OpenAI();

async function main() {
  const stream = await openai.chat.completions.create({
    model: 'gpt-3.5-turbo',
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
    Authorization: `Bearer ${YOUR KEY}`,
    ...formData.getHeaders(),
  },
  body: formData,
});

const responseData = await response.json();

console.log(responseData) // {"text": "hello"}

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
    print(chunk.choices[0].message.content or "", end="")

```
### Whisper

```python

import requests

API_KEY = 'YOUR_KEY'  
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

### List of all available models:
1000⚡️ = 0.8 RUB = 0,009 USD

- `gpt-4o`: 1000 tokens = 1000⚡️
- `gpt-4o-mini`: 1000 tokens = 70⚡️
- `gpt-3.5-turbo`: 1000 tokens = 70⚡️
- `meta-llama/Meta-Llama-3.1-405B`: 1000 tokens = 800⚡️
- `meta-llama/Meta-Llama-3.1-70B`: 1000 tokens = 285⚡️
- `meta-llama/Meta-Llama-3-70B-Instruct`: 1000 tokens = 285⚡️
- `meta-llama/Meta-Llama-3.1-8B`: 1000 tokens = 20⚡️

### Whisper price
- `whisper-1`: 1 minute = 6000⚡️
