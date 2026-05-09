from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Sirf BOT_TOKEN lagana hai
BOT_TOKEN = 

# Font styles (lightweight)
fonts = {
    "bold": str.maketrans("abcdefghijklmnopqrstuvwxyz", "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘵𝘶𝘷𝘄𝘹𝘆𝘇"),
    "italic": str.maketrans("abcdefghijklmnopqrstuvwxyz", "𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻"),
    "mono": str.maketrans("abcdefghijklmnopqrstuvwxyz", "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣")
}

# Start command
def start(update, context):
    update.message.reply_text(
        "👋 Welcome to Simple Fontify Bot!\n\n"
        "Use /help to see available commands.\n"
        "Try: /font bold hello"
    )

# Help command
def help_cmd(update, context):
    update.message.reply_text(
        "📖 Available Commands:\n"
        "/start - Welcome message\n"
        "/help - Show this help\n"
        "/font style text - Convert text into font\n\n"
        "Available styles: bold, italic, mono"
    )

# Font command
def fontify(update, context):
    try:
        style = context.args[0]
        text = " ".join(context.args[1:])
        if style in fonts:
            converted = text.translate(fonts[style])
            update.message.reply_text(f"**{style} font:**\n{converted}")
        else:
            update.message.reply_text("❌ Invalid style!\nAvailable: bold, italic, mono")
    except:
        update.message.reply_text("Usage: /font style text\nExample: /font bold hello")

# Echo fallback
def echo(update, context):
    update.message.reply_text(f"🗣 You said: {update.message.text}")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CommandHandler("font", fontify))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()