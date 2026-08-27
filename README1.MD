# 🤖 Daily Planner AI Telegram Bot

> برای ادامه دادن با زبان فارسی [کلیک کنید](README.fa.md).

An AI-powered Telegram bot that builds smart, realistic daily study/task schedules, tracks daily mood, energy, and test results, and automatically reports progress to a consultant/mentor group — all with full Persian (Jalali) calendar support.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-20%2B-2CA5E0?logo=telegram&logoColor=white)
![SQLite](https://img.shields.io/badge/Database-SQLite-07405E?logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## ✨ Features

- **🧠 AI-Generated Schedules** — Automatically builds a logical, time-boxed daily schedule from your task list, with a smart fallback chain across three AI providers:
  1. **Google Gemini** (`gemini-1.5-flash`)
  2. **OpenRouter** (free Qwen model)
  3. **python-tgpt** (free, no API key required)
  4. A built-in rule-based scheduler as the final fallback, so the bot **never fails to produce a schedule**.
- **📅 Persian (Jalali) Calendar Support** — All dates, plans, and reports are handled using the Jalali calendar via `jdatetime`.
- **🗂️ Multi-Day Plans** — Create study/work plans spanning multiple days, each with its own task list.
- **📊 Daily Check-in & Reporting** — Users log wake/sleep time, mood, energy level, and practice-test results (correct/wrong/accuracy).
- **👥 Consultant Group Reports** — Link a Telegram group as a "consultant" channel; the bot automatically sends each user's daily report there every night (23:00 Tehran time), or on demand via `/ft`.
- **🔐 Role-Based Access Control** — `owner`, `admin`, and `user` roles. New users must be approved by the owner, or the owner can claim their role with a secret token.
- **💾 Persistent Storage** — All data (users, plans, tasks, logs, states) is stored in a local SQLite database (`planner.db`).
- **🖱️ Inline Keyboard Menu** — Fully interactive, button-driven UI — no need to memorize commands.

---

## 🛠️ Tech Stack

| Component | Library |
|---|---|
| Telegram Bot Framework | [`python-telegram-bot`](https://github.com/python-telegram-bot/python-telegram-bot) |
| HTTP Client | `httpx` |
| Jalali Calendar | `jdatetime` |
| AI — Google Gemini | `google-generativeai` |
| AI — OpenRouter | `openai` (OpenRouter-compatible client) |
| AI — Free fallback | `python-tgpt` |
| Environment Variables | `python-dotenv` |
| Database | `sqlite3` (built-in) |

---

## 🤖 Bot Commands

| Command | Description | Access |
|---|---|---|
| `/start` | Start the bot / open the main menu | Everyone |
| `/claimtoken <token>` | Claim ownership of the bot with the secret `OWNER_TOKEN` | Everyone (once) |
| `/adduser <@username\|id>` | Grant a user access to the bot | Owner only |
| `/setgroup` | Set the current group as this user's consultant/report group (run **inside** the group) | Authorized users |
| `/cleargroup` | Remove the linked consultant group | Authorized users |
| `/ft` | Force-send today's report to the consultant group right now | Authorized users |
| `/state` | Show the current conversation state (debugging) | Authorized users |
| `/debug` | Show internal debug information | Authorized users |

---

## 📋 Requirements

- Python **3.10+**
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- (Optional, but recommended) a free API key for **at least one** AI provider:
  - [Google AI Studio](https://aistudio.google.com/) → Gemini API key
  - [OpenRouter](https://openrouter.ai/) → API key
  - If neither is set, the bot automatically falls back to `python-tgpt` (free) and, ultimately, a built-in rule-based scheduler.

---

## 🚀 Installation

Choose whichever setup fits you best.

### Method 1 — VPS / Self-Hosted PC

Run the bot yourself on a Linux VPS, a Windows/Linux/macOS PC, or a Raspberry Pi.

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-username>/<your-repo>.git
   cd <your-repo>
   ```

2. **Create and activate a virtual environment** (recommended)
   ```bash
   python3 -m venv venv
   # Linux / macOS
   source venv/bin/activate
   # Windows
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Copy the example file and fill in your own values:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` (see the [Configuration](#-configuration) table below).

5. **Run the bot**
   ```bash
   python bot.py
   ```

6. **Keep it running 24/7 (VPS only)**

   Since a Telegram bot needs to run continuously, use a process manager so it survives reboots and SSH disconnects. Pick one:

   - **screen / tmux** (quick & simple)
     ```bash
     screen -S telegram-bot
     python bot.py
     # detach with Ctrl+A then D
     ```
   - **pm2** (recommended for production)
     ```bash
     npm install -g pm2
     pm2 start bot.py --interpreter python3 --name daily-planner-bot
     pm2 save
     pm2 startup
     ```
   - **systemd service** (most robust on Linux)
     ```ini
     # /etc/systemd/system/daily-planner-bot.service
     [Unit]
     Description=Daily Planner Telegram Bot
     After=network.target

     [Service]
     WorkingDirectory=/path/to/your-repo
     ExecStart=/path/to/your-repo/venv/bin/python bot.py
     Restart=always
     User=your-linux-user

     [Install]
     WantedBy=multi-user.target
     ```
     ```bash
     sudo systemctl daemon-reload
     sudo systemctl enable --now daily-planner-bot
     ```

### Method 2 — PaaS (Python hosting platforms)

Deploy without managing a server, using any Python-friendly PaaS (e.g. Railway, Render, Heroku-style platforms, or similar).

1. **Push this repository to GitHub** (see the [Push to GitHub](#-pushing-to-github) section below).
2. **Create a new Python service** on your PaaS of choice and connect it to your GitHub repository.
3. **Set the start command** to:
   ```bash
   python bot.py
   ```
4. **Add environment variables** from the [Configuration](#-configuration) table in your PaaS dashboard (do **not** upload your `.env` file — set the variables directly in the platform's settings).
5. **Enable a persistent disk/volume** for the app's working directory if your platform supports it, so `planner.db` (SQLite) isn't wiped on every redeploy. If your PaaS uses an ephemeral filesystem, consider mounting a volume at the bot's working directory.
6. **Deploy.** The platform will install `requirements.txt` automatically and start the bot.

> 💡 The bot uses long polling (`app.run_polling()`), so no public URL, domain, or webhook configuration is required — it works on any platform that can simply keep a Python process running.

---

## ⚙️ Configuration

Create a `.env` file in the project root (see `.env.example`) with the following variables:

| Variable | Required | Description |
|---|:---:|---|
| `BOT_TOKEN` | ✅ | Your Telegram bot token from [@BotFather](https://t.me/BotFather) |
| `GEMINI_API_KEY` | ⬜ | Google Gemini API key (must start with `AIza`) — enables AI scheduling via Gemini |
| `OPENROUTER_API_KEY` | ⬜ | OpenRouter API key (must start with `sk-or`) — used if Gemini isn't configured |
| `CONSULTANT_GROUP_ID` | ⬜ | Default consultant group chat ID (can also be set per-user via `/setgroup`) |
| `OWNER_USERNAME` | ✅ | Telegram **username** (without `@`) of the bot owner |
| `OWNER_TOKEN` | ✅ | A secret token used once with `/claimtoken <token>` to claim the owner role |

> ⚠️ **Never commit your real `.env` file to GitHub.** Keep secrets out of version control — this repo's `.gitignore` already excludes `.env`.

---

## 📤 Pushing to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

Make sure `.env` is listed in `.gitignore` before your first commit so your bot token and API keys are never exposed publicly.

---

## 📁 Project Structure

```
.
├── bot.py              # Main bot application (handlers, AI logic, database, scheduler)
├── requirements.txt    # Python dependencies
├── .env.example         # Example environment variables (copy to .env)
├── planner.db           # SQLite database (auto-created on first run)
├── README.md             # English documentation (this file)
└── README.fa.md          # Persian (فارسی) documentation
```

---

## 🧩 How It Works — Quick Overview

1. A user sends `/start` and, once approved by the owner (or via `/claimtoken`), gets access to the main menu.
2. They create a multi-day **plan** with a title, date range, and tasks for each day.
3. Each day, the user submits a **daily check-in**: wake/sleep time, mood, energy, and practice-test results.
4. The AI handler generates a personalized, time-boxed **schedule** for the day's tasks (breaks, lunch, prayer time, and study-session limits are all factored in).
5. At 23:00 Tehran time, the bot automatically compiles and sends a **daily report** to the user's linked consultant group — or the user can trigger it instantly with `/ft`.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙋 Support

If you run into issues, please open an [issue](../../issues) on this repository.
