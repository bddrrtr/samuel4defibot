import os
import logging
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
JOIN, WALLET = range(2)

# Get environment variables
API_TOKEN = os.getenv('API_TOKEN')
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME')
GROUP_USERNAME = os.getenv('GROUP_USERNAME')
TWITTER_USERNAME = os.getenv('TWITTER_USERNAME')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send instructions and join links"""
    keyboard = [
        [InlineKeyboardButton("Channel", url=f"https://t.me/{CHANNEL_USERNAME}")],
        [InlineKeyboardButton("Group", url=f"https://t.me/{GROUP_USERNAME}")],
        [InlineKeyboardButton("Twitter", url=f"https://twitter.com/{TWITTER_USERNAME}")],
        [InlineKeyboardButton("I've Joined ✅", callback_data="joined")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📢 Join our channels to participate in the airdrop:\n\n"
        f"- Channel: {CHANNEL_USERNAME}\n"
        f"- Group: {GROUP_USERNAME}\n"
        f"- Twitter: {TWITTER_USERNAME}\n\n"
        "Click the buttons below to join, then press ✅",
        reply_markup=reply_markup
    )
    return JOIN

async def joined(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask for SOL wallet after user claims they've joined"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🎉 Great! Now send me your SOL wallet address:",
        reply_markup=None
    )
    return WALLET

async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process wallet address and send confirmation"""
    wallet_address = update.message.text
    await update.message.reply_text(
        f"🚀 Congratulations! 10 SOL is on its way to your wallet:\n\n"
        f"`{wallet_address}`\n\n"
        "Note: This is a mock airdrop - no actual SOL will be sent.",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation"""
    await update.message.reply_text(
        "Action cancelled. Use /start to begin again.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main() -> None:
    """Run the bot"""
    application = Application.builder().token(API_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            JOIN: [CallbackQueryHandler(joined, pattern='^joined$')],
            WALLET: [MessageHandler(filters.TEXT & ~filters.COMMAND, wallet)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
