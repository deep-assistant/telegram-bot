# Case Study: Issue #152 - Images Not Recognized as Task

## Issue Overview

**Issue:** [#152](https://github.com/deep-assistant/telegram-bot/issues/152)  
**Title:** Images sent to bot are not recognized as a task, user is unable to get solution of the task by example  
**Reported by:** @konard  
**Status:** Open  
**Labels:** bug  

## Problem Statement

Users send images to the Telegram bot with text like "Реши по примеру" (Solve by example), expecting the AI to analyze the images and provide solutions. However, the bot responds with a generic message asking for clarification, completely ignoring the images that were sent.

## Timeline of Events

### User Action (as shown in screenshot1.png)

1. **User "Наталия Мокрая"** sends:
   - Two images containing:
     - A numbered list of anatomical structures (in Russian)
     - A handwritten notebook page with anatomical notes
   - Text caption: **"Реши по примеру"** (Solve by example)

2. **Bot Response** (from @DeepGPTBot):
   > "Hello there! I noticed that your message doesn't include a specific question or topic. Could you please clarify what you'd like assistance with or provide more details? I'm here to help with any inquiry you have, whether it's a complex issue or something simple. Just let me know how I can support your career or any project you're working on."

### What the User Expected

The user expected the bot to:
1. Recognize that images were sent
2. Analyze the images containing the anatomical structures list and handwritten notes
3. Provide a solution or answer based on the example shown in the images

### What Actually Happened

The bot completely ignored the images and responded as if only empty text was received.

## Technical Analysis

### Root Cause Identification

#### Python Bot (`bot/gpt/router.py`)

**Handler for Photo Messages** (Lines 224-278):

```python
@gptRouter.message(Photo())
async def handle_image(message: Message, album):
    # ... validation and checks ...
    
    photos = []
    for item in album:
        photos.append(item.photo[-1])
    
    # ... token checks ...
    
    text = "Опиши" if message.caption is None else message.caption  # Line 269
    
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    content = await get_photos_links(message, photos)  # Line 273
    content.append({"type": "text", "text": text})  # Line 275
    
    await handle_gpt_request(message, content)  # Line 277
```

**Issue:** The handler correctly:
- Extracts photos from the album
- Creates image URLs using `get_photos_links()` 
- Appends the caption text
- Passes multimodal content to `handle_gpt_request()`

**The Problem is in `handle_gpt_request()` function** (Lines 83-206):

```python
async def handle_gpt_request(message: Message, text: str):  # Line 83
    # ... validation ...
    
    answer = await completionsService.query_chatgpt(
        user_id,
        text,  # <-- This is the problem!
        system_message,
        gpt_model,
        bot_model,
        questionAnswer,
    )
```

**Critical Issue:** 
- The function signature expects `text: str` (Line 83)
- But when called from photo handler, it receives `content` which is a list of dict objects: `[{"type": "image_url", "image_url": {"url": "..."}}, {"type": "text", "text": "..."}]`
- This multimodal array is passed directly to the API Gateway

#### API Gateway Integration (`services/completions_service.py`)

**Query ChatGPT function** (Lines 77-117):

```python
async def query_chatgpt(self, user_id, message, system_message, gpt_model: str, bot_model: GPTModels, singleMessage: bool) -> Any:
    params = {
        "masterToken": ADMIN_TOKEN
    }
    
    payload = {
        'userId': get_user_name(user_id),
        'content': message,  # <-- multimodal content passed here
        'systemMessage': system_message,
        'model': gpt_model
    }
    
    response = await async_post(f"{PROXY_URL}/completions", json=payload, params=params)
```

**The Real Problem:**  
The code DOES send the multimodal content to the API Gateway's `/completions` endpoint. The issue is that:

1. **The API Gateway doesn't support multimodal content in its `/completions` endpoint**
2. Or the API Gateway doesn't know how to handle image URLs in the format provided
3. Or the model selected doesn't support vision capabilities

### JavaScript Bot Comparison

The JavaScript implementation has similar code structure (`js/src/bot/gpt/router.js`):

```javascript
gptRouter.message(Photo(), async (message, album) => {
  const photos = album.map(item => item.photo[item.photo.length - 1]);
  const text = message.caption || 'Опиши';
  const content = await getPhotosLinks(message, photos);
  content.push({ type: 'text', text });
  await handleGptRequest(message, content);  // Same issue
});
```

**Same Problem:** JavaScript bot has the same architectural issue where multimodal content is sent to an endpoint that doesn't properly handle it.

## Evidence Analysis

### Image 1: Screenshot (screenshot1.png)

Shows the complete conversation where:
- User sends two photos with anatomical content
- Bot ignores the images completely
- Bot responds with generic "I don't understand" message

### Image 2: List of Anatomical Structures (image1.png)

Contains a numbered list in Russian:
1. Боковая пластинка крыловидного отростка (Lateral pterygoid plate)
2. Передняя поверхность каменистой части (Anterior surface of petrous part)
3. Гребень большого бугорка плеча (Greater tubercle crest of humerus)
... (12 items total)

### Image 3: Handwritten Notes (image2.png)

Contains handwritten anatomical notes in Russian with various terminology and references.

## Possible Reasons for Failure

### 1. **API Gateway Endpoint Limitation**
   - The `/completions` endpoint at `PROXY_URL` may not support multimodal content
   - It may expect only text content

### 2. **Missing GoAPI Integration**
   - The code has a `get_multi_modal_conversation()` function that uses GoAPI for multimodal
   - But the photo handler doesn't use it - it uses the regular completions endpoint instead

### 3. **Model Selection**
   - The current model selected might not support vision
   - Only certain models (GPT-4o, Claude with vision, etc.) support images

### 4. **Image URL Format**
   - The image URLs might need to be accessible externally
   - Telegram file URLs might require authentication

## Proposed Solutions

### Solution 1: Use GoAPI for Multimodal (Recommended for Complex Cases)

The codebase already has GoAPI integration for multimodal conversations:

```python
# services/completions_service.py has:
async def get_multi_modal_conversation(self, prompt, attempt: int = 0):
    # Uses GoAPI for handling images
```

**Modify `handle_gpt_request()` to detect multimodal content:**

```python
async def handle_gpt_request(message: Message, text):
    # ... existing code ...
    
    # Check if text is multimodal content
    if isinstance(text, list):
        # Multimodal content - use GoAPI
        answer = await completionsService.get_multi_modal_conversation(text)
        # Process answer differently
    else:
        # Text only - use regular completions
        answer = await completionsService.query_chatgpt(...)
```

### Solution 2: Update API Gateway to Support Multimodal

If we control the API Gateway, update the `/completions` endpoint to:
1. Accept multimodal content in OpenAI's format
2. Forward to appropriate model (GPT-4o, Claude Sonnet with vision)
3. Handle image URL downloads and encoding

### Solution 3: Pre-process Images with Vision API

Before sending to regular completions:
1. Download images from Telegram
2. Send to vision-capable model to get description
3. Append description to user's text
4. Send combined text to regular completions endpoint

```python
async def handle_image(message: Message, album):
    photos = []
    for item in album:
        photos.append(item.photo[-1])
    
    # Get image descriptions
    image_descriptions = []
    for photo in photos:
        file_info = await message.bot.get_file(photo.file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
        
        # Use vision API to describe image
        description = await get_image_description(file_url)
        image_descriptions.append(description)
    
    # Combine with user text
    user_text = message.caption or "Опиши эти изображения"
    combined_text = f"{user_text}\n\nИзображения содержат:\n" + "\n".join(image_descriptions)
    
    # Send as regular text
    await handle_gpt_request(message, combined_text)
```

### Solution 4: Direct OpenAI API Call with Vision

Use OpenAI's vision API directly for photo messages:

```python
from openai import OpenAI

async def handle_image(message: Message, album):
    photos = []
    for item in album:
        photos.append(item.photo[-1])
    
    # Build OpenAI vision API request
    content = []
    for photo in photos:
        file_info = await message.bot.get_file(photo.file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
        content.append({
            "type": "image_url",
            "image_url": {"url": file_url}
        })
    
    text = message.caption or "Опиши эти изображения"
    content.append({"type": "text", "text": text})
    
    # Call OpenAI directly
    client = OpenAI(api_key=..., base_url=f"{PROXY_URL}/v1/")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": content}
        ]
    )
    
    await message.answer(response.choices[0].message.content)
```

## Recommended Implementation Plan

1. **Investigate API Gateway Capabilities**
   - Check if `/completions` endpoint supports multimodal
   - Check which models are available with vision capabilities
   - Test with multimodal payload

2. **Implement Fix Based on Findings**
   - If API Gateway supports multimodal: Update payload format and ensure proper model selection
   - If not: Use GoAPI integration or implement Solution 3/4

3. **Add Tests**
   - Create automated test that sends photo message
   - Verify bot recognizes and processes images
   - Test in both Python and JavaScript implementations

4. **Add Tracing/Logging**
   - Log when multimodal content is detected
   - Log which endpoint/API is being used
   - Add debug flag to enable verbose multimodal processing logs

5. **Update Documentation**
   - Document how image processing works
   - Document which models support vision
   - Add troubleshooting guide for image-related issues

## Impact Assessment

### Severity: **HIGH**
- Users cannot get help with visual homework/tasks
- Core bot functionality is broken for multimodal use cases
- Affects both Python and JavaScript implementations

### User Impact:
- Students trying to get help with homework images
- Users wanting to analyze documents, diagrams, photos
- Anyone trying to use "solve by example" with visual references

### Technical Debt:
- Code structure exists for multimodal but isn't wired correctly
- Multiple possible solutions but unclear which is correct
- Needs investigation into API Gateway capabilities

## Conclusion

The bot has the infrastructure to handle images (photo handler, multimodal content structure, GoAPI integration) but these pieces aren't properly connected. The photo handler sends multimodal content to an endpoint that either:
1. Doesn't support multimodal format
2. Doesn't route to vision-capable models
3. Isn't configured correctly

The fix requires either:
- Updating how the API Gateway handles multimodal content, OR
- Routing photo messages through GoAPI integration, OR  
- Pre-processing images into text descriptions

All three solutions are viable; the choice depends on API Gateway capabilities and performance requirements.
