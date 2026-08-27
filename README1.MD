# 🤖 Telegram Planner Bot – Smart Planning Bot

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)
![SQLite](https://img.shields.io/badge/Database-SQLite-green?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-yellow)

> **Telegram bot for daily planning, task management, test logging, sending reports to consultants, and AI support**

---

## 📖 Introduction

This bot helps you manage **long-term** plans with **daily** tasks, track your progress, log and analyze daily tests, and send **automated** reports to your **consultant**.

**Key Features:**
- ✅ Long-term planning with start/end dates and custom tasks for each day
- ✅ Smart time distribution based on difficulty level (using AI)
- ✅ Daily report logging (wake-up time, sleep time, mood, energy, custom questions)
- ✅ Daily task management (mark as done/pending)
- ✅ Daily test logging (total tests, wrong answers, accuracy percentage)
- ✅ Automatic report sending to consultant every night at 11 PM Tehran time
- ✅ Instant report sending with `/ft` command
- ✅ Consultant group configuration for report delivery
- ✅ AI support (Gemini, OpenRouter, python-tgpt) for daily schedule generation
- ✅ User management system (owner, admin, regular user)
- ✅ Automatic notification to owner when new users start the bot
- ✅ `/adduser` command for owner to grant access to new users
- ✅ SQLite database for permanent data storage

---

## 🚀 Installation and Setup Methods

### Method 1: Local Installation (VPS or Local Machine)

#### 1. Prerequisites

- Python 3.10 or higher
- pip
- A Telegram bot (created via [@BotFather](https://t.me/BotFather))
- API keys (optional) for AI services

#### 2. Installation

```bash
# Clone the repository
git clone https://github.com/your-username/telegram-planner-bot.git
cd telegram-planner-bot
pip install -r requirements.txt
