<div align="center">

# flParser

### A Telegram bot that watches [fl.ru](https://www.fl.ru) and delivers fresh freelance projects (free orders) to a Telegram chat.

<p>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white">
  <img alt="aiogram" src="https://img.shields.io/badge/aiogram-3.x-2CA5E0?logo=telegram&logoColor=white">
  <img alt="uv" src="https://img.shields.io/badge/built%20with-uv-DE5FE9?logo=astral&logoColor=white">
  <img alt="SQLite" src="https://img.shields.io/badge/storage-SQLite-003B57?logo=sqlite&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green">
</p>

</div>

---

## ! Quick start

This project uses [**uv**](https://github.com/astral-sh/uv) for dependency and environment management.

```bash
# 1. Clone and enter the project
git clone <https://github.com/vander00/fl.ru-parser> flparser && cd flparser

# 2. Create and activate a virtual environment (Python 3.13+ required)
python3.13 -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -e .
---
# Or you can use uv if you have it installed
# $ uv sync

# 4. Configure your credentials
cp .env.example .env
# edit .env and set BOT_TOKEN and TELEGRAM_CHAT_ID (the id of your Telegram account)

# 5. Run the bot
python main.py
```

Then open Telegram, message your bot `/start`, and pick a category. 

> **Getting your credentials:** create a bot with [@BotFather](https://t.me/BotFather) to get `BOT_TOKEN`, and use a bot like [@userinfobot](https://t.me/userinfobot) to find your `TELEGRAM_CHAT_ID`.

---

## Configuration

All configuration is read from environment variables (via a `.env` file). Only the first two are required.

| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `BOT_TOKEN` | Yes | — | Telegram bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Yes | — | Chat ID that receives project notifications |
| `POLL_INTERVAL_SECONDS` | | `300` | How often to re-scrape fl.ru |
| `MAX_PAGES` | | `2` | How many listing pages to scan per poll |
| `CATEGORIES` | | — | The categories slug to subscribe to on startup (e.g. `programmirovanie saity`) |
| `DB_PATH` | | `flparser.db` | Path to the SQLite seen-projects store |
| `LOG_LEVEL` | | `INFO` | Logging verbosity |
| `LOG_FILE` | | `bot.log` | Rotating log file path |

---

**After 30 days** stale seen-entries are purged automatically.

---

## Built with

[aiogram](https://docs.aiogram.dev/) · [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) · [requests](https://requests.readthedocs.io/) · [python-dotenv](https://github.com/theskumar/python-dotenv) · SQLite · [uv](https://github.com/astral-sh/uv)

---
