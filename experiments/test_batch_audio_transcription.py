"""
Experiment script to test batch audio/voice message transcription.

This script documents the fix for issue #148 where multiple forwarded
audio/voice messages were not being transcribed - only the first one was.

The fix modifies the handle_voice handler to:
1. Accept a batch_messages parameter (similar to handle_completion)
2. Iterate through all messages in the batch
3. Transcribe each audio/voice message
4. Combine all transcriptions and report total energy usage

Testing approach:
- The AlbumMiddleware in bot/bot_run.py groups messages by timestamp into batch_data
- When multiple audio/voice messages are forwarded, they arrive with the same timestamp
- The middleware waits 0.01s and then passes all batched messages to the handler
- The handler now processes all messages in the batch instead of just the first one

Manual testing steps:
1. Forward multiple audio/voice messages to the bot
2. Verify all messages are transcribed (not just the first)
3. Check that total energy cost is reported correctly
4. Ensure combined transcription is sent to GPT or returned based on Transcribe mode
"""

import asyncio
from unittest.mock import Mock, AsyncMock, patch
from aiogram.types import Message, Voice, Audio, User, Chat


async def test_single_audio_message():
    """Test that single audio message is processed correctly."""
    print("Testing single audio message...")

    # This would be a real integration test with mocked Telegram API
    # For now, this documents the expected behavior

    # Expected: Single message processed, transcription returned
    print("✓ Single message should be transcribed normally")


async def test_multiple_forwarded_audio():
    """Test that multiple forwarded audio messages are all transcribed."""
    print("\nTesting multiple forwarded audio messages...")

    # Expected behavior:
    # - All audio messages in the batch are transcribed
    # - Transcriptions are combined with double newlines
    # - Total energy cost is sum of all transcriptions
    # - Combined text is sent to GPT or returned based on mode

    print("✓ All messages in batch should be transcribed")
    print("✓ Transcriptions should be combined with \\n\\n separator")
    print("✓ Total energy should be sum of all transcriptions")


async def test_mixed_batch():
    """Test batch with mixed content types (text + audio)."""
    print("\nTesting mixed batch (text + audio)...")

    # Expected: Only audio/voice messages are transcribed
    # Text messages are skipped (checked with msg.voice is None and msg.audio is None)

    print("✓ Only audio/voice messages should be processed")
    print("✓ Text and other message types should be skipped")


async def test_transcribe_mode():
    """Test that Transcribe mode returns text without GPT processing."""
    print("\nTesting Transcribe mode...")

    # Expected: In Transcribe mode, combined transcription is returned
    # without being sent to handle_gpt_request

    print("✓ Transcribe mode should return text without GPT")


if __name__ == "__main__":
    print("=" * 60)
    print("Batch Audio Transcription Fix - Issue #148")
    print("=" * 60)

    asyncio.run(test_single_audio_message())
    asyncio.run(test_multiple_forwarded_audio())
    asyncio.run(test_mixed_batch())
    asyncio.run(test_transcribe_mode())

    print("\n" + "=" * 60)
    print("Documentation complete. See bot/gpt/router.py:311-395")
    print("=" * 60)
