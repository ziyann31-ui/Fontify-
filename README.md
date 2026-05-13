<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Telegram-Bot-2CA5E0?style=flat-square&logo=telegram" alt="Telegram">
  <img src="https://img.shields.io/badge/MongoDB-Atlas-47A248?style=flat-square&logo=mongodb" alt="MongoDB">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Render-Deploy-46E3B7?style=flat-square&logo=render" alt="Render">
</p>

<h1 align="center">🎨 Fontify Bot</h1>

<p align="center">
  <b>Transform your boring text into 37+ amazing stylish fonts!</b><br>
  A powerful, open-source Telegram bot built with Python & MongoDB.
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-demo">Demo</a> •
  <a href="#-deployment">Deploy</a> •
  <a href="#-owner-commands">Owner</a> •
  <a href="#-fork--star">Fork</a>
</p>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔤 **37+ Font Styles** | Bold, Italic, Cursive, Fraktur, Monospace, Zalgo, Glitch, Bubble, Matrix, Runic, Morse, and more! |
| 📂 **Smart Categories** | Fonts organized into Bold, Cursive, Small, Symbols, Fancy, Glitch groups |
| 📊 **User Stats** | Track your personal usage count and join date |
| 👥 **Group Support** | Works in groups — just mention the bot or reply to its message |
| 🎉 **One-Tap Copy** | Tap the styled text to copy it instantly |
| 🗄️ **MongoDB Backend** | Robust database for users, groups & usage logs |
| 📢 **Broadcast** | Owner can broadcast messages to all users & groups |

---

## 🎨 Font Preview

| Style | Example |
|-------|---------|
| **Bold** | 𝐇𝐞𝐥𝐥𝐨 𝐖𝐨𝐫𝐥𝐝 |
| **Italic** | 𝐻𝑒𝑙𝑙𝑜 𝑊𝑜𝑟𝑙𝑑 |
| **Cursive** | 𝓗𝓮𝓵𝓵𝓸 𝓦𝓸𝓻𝓵𝓭 |
| **Fraktur** | ℌ𝔢𝔩𝔩𝔬 𝔚𝔬𝔯𝔩𝔡 |
| **Double Struck** | ℍ𝕖𝕝𝕝𝕠 𝕎𝕠𝕣𝕝𝕕 |
| **Monospace** | 𝙷𝚎𝚕𝚕𝚘 𝚆𝚘𝚛𝚕𝚍 |
| **Zalgo** | H̷̛̗e̷̘̚l̷̙̚l̷̛̗o̷̙̚ |
| **Bubble** | ꒒ꋰ꒒꒯ ꅐꂦꋪ꒒꒯ |
| **Matrix** | 卄乇ㄥㄥㄖ 山ㄖ尺ㄥㄗ |
| **Morse** | .... . .-.. .-.. --- / .-- --- .-. .-.. -.. |

> 💡 *And 27+ more styles!*

---

## 🚀 Deployment

### 🌟 Method 1: Deploy on Render (Recommended)

1. **Fork this repo** — Click the 🍴 Fork button on top right
2. **Create a free Render account** at [render.com](https://render.com)
3. **New → Background Worker**
4. **Connect your GitHub repo**
5. **Add Environment Variables** in Render Dashboard:
   - `BOT_TOKEN` — Get from [@BotFather](https://t.me/BotFather)
   - `MONGO_URI` — Get from [MongoDB Atlas](https://www.mongodb.com/atlas)
   - `OWNER_ID` — Your Telegram numeric ID
   - `BOT_USERNAME` — Your bot's username (without @)
6. **Deploy** ✅

> `render.yaml` is included for Blueprint auto-configuration.

---

### 🐳 Method 2: Deploy with Docker

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/fontify-bot.git
cd fontify-bot

# Build & run
docker build -t fontify-bot .
docker run -d --env-file .env fontify-bot
```

---

### ☁️ Method 3: Deploy on Heroku

1. **Fork this repo**
2. **Create Heroku app**
3. **Add Config Vars** in Settings tab:
   - `BOT_TOKEN`, `MONGO_URI`, `OWNER_ID`, `BOT_USERNAME`
4. **Deploy via GitHub** or CLI:

```bash
heroku create your-bot-name
heroku config:set BOT_TOKEN=xxx MONGO_URI=xxx OWNER_ID=xxx
heroku stack:set container   # if using Dockerfile
# OR
heroku buildpacks:set heroku/python
git push heroku main
```

> `Procfile` & `runtime.txt` are included for Heroku.

---

### 💻 Method 4: Local Run

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/fontify-bot.git
cd fontify-bot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup env
cp .env.example .env
# Edit .env with your credentials

# 4. Run
python bot.py
```

---

## 🔧 Environment Variables

| Variable | How to Get | Required |
|----------|-----------|----------|
| `BOT_TOKEN` | [@BotFather](https://t.me/BotFather) → `/newbot` | ✅ |
| `MONGO_URI` | [MongoDB Atlas](https://www.mongodb.com/atlas) → Connect → Drivers → Python | ✅ |
| `OWNER_ID` | [@userinfobot](https://t.me/userinfobot) → Send any message | ✅ |
| `BOT_USERNAME` | The username you set in BotFather (without @) | ✅ |

---

## 👑 Owner Commands

> ⚠️ These commands work **only** for the bot owner (`OWNER_ID`)

| Command | Usage | Description |
|---------|-------|-------------|
| `/stats` | `/stats` | Global stats: total users, usage, today's activity + Top 5 users |
| `/users` | `/users` | Top 10 most active users with names & usage count |
| `/broadcast` | `/broadcast Hello everyone!` | Send a message to **all** users & groups |

---

## 🍴 Fork & Star

Love this project? Show some support!

### ⭐ Star this Repo
1. Click the **⭐ Star** button on the top right of this page
2. It helps others discover this project!

### 🍴 Fork this Repo
1. Click the **🍴 Fork** button (top right)
2. This creates your own copy of the project
3. Now you can customize it freely!

### 🔄 Keep Your Fork Updated

```bash
# Add upstream remote (do this once)
git remote add upstream https://github.com/ORIGINAL_OWNER/fontify-bot.git

# Fetch latest changes
git fetch upstream

# Merge into your main branch
git checkout main
git merge upstream/main

# Push to your fork
git push origin main
```

---

## 📁 Project Structure

```
fontify-bot/
├── bot.py              # Main bot code
├── requirements.txt    # Python dependencies
├── render.yaml         # Render.com config
├── Dockerfile          # Docker container config
├── Procfile            # Heroku worker config
├── runtime.txt         # Python version for Heroku
├── .env.example        # Environment variables template
└── README.md           # This file
```

---

## 📦 Tech Stack

- **python-telegram-bot** v20.7 — Telegram Bot API wrapper
- **pymongo** — MongoDB driver
- **MongoDB Atlas** — Cloud database
- **Render / Heroku / Docker** — Deployment platforms

---

## 🤝 Contributing

1. 🍴 Fork this repository
2. 🌿 Create a new branch (`git checkout -b feature/amazing-feature`)
3. ✍️ Commit your changes (`git commit -m 'Add amazing feature'`)
4. 📤 Push to the branch (`git push origin feature/amazing-feature`)
5. 🔁 Open a Pull Request

---

## 📜 License

This project is open-source and available under the **MIT License**.

---

<p align="center">
  <b>Made with ❤️ for the Telegram community</b><br>
  <a href="https://t.me/BotFather">Get your bot token</a> • 
  <a href="https://render.com">Deploy on Render</a>
</p>