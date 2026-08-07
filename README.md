# 🚨 TG Alarm — Emergency Telegram Voice Call & Alert System

A high-reliability automated alerting and VoIP call trigger system for Telegram. Designed to monitor critical incoming signals from specified bots, users, channels, or groups in real time, waking the user up with an **unmissable full-screen Telegram voice call** during sleep hours.

---

## ✨ Features

- 📡 **Real-Time MTProto Monitoring (`monitor.py`)**: Sub-millisecond interception of incoming messages via Telegram MTProto Userbot protocol, bypassing UI mute settings.
- 📱 **Interactive Telegram Admin Control Panel (`admin_bot.py`)**: Built with `aiogram 3.x`, offering inline keyboard control:
  - 💤 **Sleep Mode ON**: Automatically initiates ringing Telegram Voice Calls for any new alert.
  - ☀️ **Awake Mode ON**: Pauses calls, sending quiet notifications.
  - ⏳ **Smart Wake Timers (2h / 4h / 8h)**: Temporarily disables calls during work hours and automatically re-enables Sleep Mode afterwards.
- 🎯 **Dynamic Target Management**: Add or remove monitored targets (bots, channels, users) dynamically directly from the Telegram Admin Bot without editing code or restarting services.
- 📞 **Native Telegram VoIP Call Dispatcher (`alerter.py`)**: Low-level Diffie-Hellman (SHA-256) VoIP call handshake caller triggering native iOS/Android incoming call screens.
- 🔒 **Isolated Security Architecture**: Runs on a restricted secondary "watcher" account on VPS, keeping your primary Telegram account and financial assets 100% off the remote server.

---

## 🛠 Project Structure

```
TG_ALARM/
├── admin_bot.py         # Telegram Admin Bot (aiogram 3.x control panel)
├── monitor.py           # MTProto Userbot listener (Telethon)
├── alerter.py           # VoIP call dispatcher & notification formatter
├── state_manager.py     # JSON state persistence & auto-wake timers
├── config.py            # Environment variable loader
├── setup_auth.py        # One-time Telegram MTProto session authenticator
├── deploy_remote.py     # 1-Click automated remote Linux VPS deployment
├── ecosystem.config.js  # PM2 process manager configuration
├── requirements.txt     # Python production dependencies
└── ops/                 # Desktop batch scripts for Windows (Status, Restart, Logs, Deploy)
```

---

## 🚀 Quick Start & Installation

### 1. Environment Setup
Copy `.env.example` to `.env` and fill in your credentials:

```env
# Primary Watcher Account Credentials (MTProto)
TG_API_ID=12345678
TG_API_HASH=your_api_hash
TG_PHONE=+10000000000

# Target bot(s) or username(s) to monitor
TARGET_BOT_USERNAME=@example_signal_bot

# Telegram Admin Bot Token (from @BotFather)
ADMIN_BOT_TOKEN=1234567890:AAA...
ADMIN_CHAT_ID=your_telegram_user_id
```

### 2. Session Authorization
Run the one-time authentication script locally to generate the `.session` file:

```bash
python setup_auth.py
```

### 3. Deploy to Linux VPS
Deploy the application to your remote Linux server under PM2 process manager:

```bash
python deploy_remote.py
```
*(Or double-click `ops/deploy.bat` on Windows)*

---

## 📄 License

MIT License. Designed for high availability and open-source portfolio demonstration.
