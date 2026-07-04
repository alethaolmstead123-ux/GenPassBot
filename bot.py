import os
import random
import string
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Get token from Railway environment variables
TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    print("❌ ERROR: BOT_TOKEN environment variable not found!")
    print("Please add BOT_TOKEN in Railway Variables tab")
    sys.exit(1)

print(f"✅ BOT_TOKEN loaded successfully (length: {len(TOKEN)})")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message with options."""
    keyboard = [
        [InlineKeyboardButton("🔐 Generate Password (12 chars)", callback_data="gen_12")],
        [InlineKeyboardButton("🔑 Generate Password (20 chars)", callback_data="gen_20")],
        [InlineKeyboardButton("🔒 Generate Password (32 chars)", callback_data="gen_32")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🔐 **Password Generator Bot**\n\n"
        "Choose a password length below, or use /gen <length>\n"
        "Example: /gen 16",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def generate_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate a password with the given length."""
    try:
        length = int(context.args[0]) if context.args else 12
        if length < 4:
            await update.message.reply_text("⚠️ Password must be at least 4 characters.")
            return
        if length > 128:
            await update.message.reply_text("⚠️ Maximum length is 128 characters.")
            return
    except (ValueError, IndexError):
        await update.message.reply_text("⚠️ Please provide a number: /gen 16")
        return

    password = generate_secure_password(length)
    await update.message.reply_text(
        f"🔐 **Your Password ({length} chars):**\n\n`{password}`",
        parse_mode="Markdown"
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button presses."""
    query = update.callback_query
    await query.answer()

    length = int(query.data.split("_")[1])
    password = generate_secure_password(length)

    await query.edit_message_text(
        f"🔐 **Your Password ({length} chars):**\n\n`{password}`\n\nGenerate another:",
        reply_markup=query.message.reply_markup,
        parse_mode="Markdown"
    )

def generate_secure_password(length: int) -> str:
    """Generate a secure random password."""
    characters = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    return ''.join(random.SystemRandom().choice(characters) for _ in range(length))

if __name__ == "__main__":
    try:
        print("🤖 Starting Password Generator Bot...")
        app = ApplicationBuilder().token(TOKEN).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("gen", generate_password))
        app.add_handler(CallbackQueryHandler(button_callback, pattern="gen_"))

        print("✅ Bot is running...")
        app.run_polling()
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        sys.exit(1)
