# CI/CD Setup

This document describes the CI/CD pipeline setup for the Telegram bot project.

## Continuous Integration (CI)

The CI pipeline runs automatically on:
- Pushes to `main` and `develop` branches
- Pull requests to `main` and `develop` branches

### CI Test
The pipeline runs a simple test (`test_ci.py`) that validates:
- Python version compatibility (3.8+)
- Required files exist
- Basic module imports
- Requirements.txt format

## Continuous Deployment (CD)

The CD pipeline deploys automatically when code is pushed to the `main` branch.

### Required Secrets
Configure these secrets in your GitHub repository settings:

- `SERVER_HOST` - Your server's IP address or hostname
- `SERVER_USER` - SSH username for deployment
- `SERVER_SSH_KEY` - Private SSH key for server access
- `SERVER_PORT` - SSH port (optional, defaults to 22)
- `DEPLOY_PATH` - Path to the project on server (optional, defaults to `/opt/telegram-bot`)

### Deployment Process
The CD pipeline:
1. SSHs into your server
2. Pulls the latest code from the main branch
3. Installs/updates Python dependencies
4. Restarts the bot service using systemctl, supervisorctl, or process restart

### Server Setup Requirements
Your server should have:
- Git repository cloned
- Python 3.8+ installed
- pip available
- SSH access configured
- Optionally: systemd service or supervisor for bot management

### Manual Deployment
You can also trigger deployment manually from the GitHub Actions tab using the "workflow_dispatch" trigger.

## Files Created
- `.github/workflows/ci.yml` - CI pipeline
- `.github/workflows/cd.yml` - CD pipeline  
- `test_ci.py` - Simple CI test
- `CI_CD_SETUP.md` - This documentation