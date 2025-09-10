# Error Reporting Setup

This bot includes an error reporting system that automatically captures and reports errors to administrators.

## Configuration

1. **Set Admin User IDs**: Add admin user IDs to your `config.py`:
   ```python
   ADMIN_USER_IDS = "123456789,987654321"  # Your Telegram user IDs
   ```

2. **Get Your User ID**: Send `/here_and_now` command to the bot to see your user ID.

## Features

### Automatic Error Reporting
- All unhandled exceptions are automatically captured
- Admins receive immediate notifications with error details
- Errors are logged to `error_reports.jsonl` file
- User-friendly error messages are sent to users

### Admin Commands

- `/errors` - Show recent error reports
- `/error_detail <number>` - Show detailed error information  
- `/error_stats` - Show error statistics
- `/clear_errors` - Clear error log
- `/test_error` - Test error reporting (triggers a test error)

### Error Information Includes

- Exception type and message
- Full traceback
- User context (ID, username, chat info)
- Message content and metadata
- Timestamp

## Usage Example

1. Configure admin user IDs in your config
2. Start the bot
3. Any error will be reported to admins
4. Use admin commands to manage errors

## Files

- `bot/error_reporting/middleware.py` - Error capturing middleware
- `bot/error_reporting/service.py` - Error reporting service
- `bot/error_reporting/router.py` - Admin commands
- `error_reports.jsonl` - Error log file (created automatically)