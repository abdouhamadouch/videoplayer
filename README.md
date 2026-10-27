# VideoPlayer Telegram Bot (free Render setup)

This repository is a small deployment wrapper for the public upstream project [antlis/tg-streaming-bot](https://github.com/antlis/tg-streaming-bot). The Docker build downloads the upstream source and installs its dependencies.

## Free-tier choices
- Render **Free Web Service** only; no paid background worker.
- Headless Chromium fallback is disabled to avoid a large optional browser install.
- Hardware transcoding is disabled; software transcoding is used where needed.
- Optional proxy, VPN sidecar, and other external paid services are not configured.

## Required Render environment variables
Set these in Render → service → Environment:
- `API_ID` — Telegram API ID
- `API_HASH` — Telegram API hash
- `BOT_TOKEN` — token from BotFather
- `BOT_USERNAME` — bot username without @
- `BOT_NAME` — display name (can be `VideoPlayer`)
- `SESSION_NAME` — Pyrogram/Kurigram session string for the assistant account
- `SUDO_USERS` — Telegram numeric user ID(s), separated by spaces

Do not put secrets in GitHub or this README.

## Important free-tier limitation
Render Free Web Services can sleep after 15 minutes without inbound traffic, and Render does not offer free background workers. This wrapper exposes a small health endpoint so the web service can start, but that does **not** guarantee the Telegram bot stays online continuously. Voice-chat streaming also depends on Telegram voice networking and may be unreliable on a free web instance. No paid resources are enabled here.

Upstream features that require extra optional setup are left off or unused, including the Chromium fallback and hardware acceleration. The upstream bot still needs a separate Telegram assistant account session, and the bot must be made an admin in the target group with the permissions described in the upstream documentation.
