from pyrogram import Client, filters

# Sirf BOT_TOKEN lagana hai
BOT_TOKEN = "8715044389:AAHaUSJZ-tEqZuB6wjHT3yCzT-CpeBw7QfU"

# Client initialize
app = Client("simple_fontify_bot", bot_token=BOT_TOKEN)

# Welcome / Start command
@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text(
        "👋 Welcome to Simple Fontify Bot!\n\n"
        "Use /help to see available commands.\n"
        "Try: /font bold hello"
    )

# Help command
@app.on_message(filters.command("help"))
def help_cmd(client, message):
    message.reply_text(
        "📖 Available Commands:\n"
        "/start - Welcome message\n"
        "/help - Show this help\n"
        "/font style text - Convert text into font\n\n"
        "Available styles: bold, italic, mono"
    )

# Lightweight font styles
fonts = {
    "bold": str.maketrans("abcdefghijklmnopqrstuvwxyz", "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘶𝘷𝘄𝘅𝘆𝘇"),
    "italic": str.maketrans("abcdefghijklmnopqrstuvwxyz", "𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻"),
    "mono": str.maketrans("abcdefghijklmnopqrstuvwxyz", "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣")
}

# Font command
@app.on_message(filters.command("font"))
def fontify(client, message):
    try:
        parts = message.text.split(" ", 2)
        style = parts[1]
        text = parts[2]
        if style in fonts:
            converted = text.translate(fonts[style])
            message.reply_text(f"**{style} font:**\n{converted}")
        else:
            message.reply_text("❌ Invalid style!\nAvailable: bold, italic, mono")
    except:
        message.reply_text("Usage: /font style text\nExample: /font bold hello")

# Echo fallback
@app.on_message(filters.text & ~filters.command(["start","help","font"]))
def echo(client, message):
    message.reply_text(f"🗣 You said: {message.text}")

# Run bot
app.run()