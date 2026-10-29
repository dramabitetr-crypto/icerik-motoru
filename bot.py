import os
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "9119725211:AAEZ79N0n7ugM45QhR_z3wmEP1AnA0TtqXs"

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Sunucusu Aktif ve Calisiyor!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "🚀 *Icerik Uretim Komuta Merkezine Hos Geldin!* 🚀\n\n"
        "Bana sadece bir konu yaz, gerisini bana birak!"
    )
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = update.message.text
    
    status_message = await update.message.reply_text(
        f"⏳ *Konu alindi:* '{topic}'\n\n"
        "1. Adim: Yapay zeka hikayeyi yaziyor...",
        parse_mode='Markdown'
    )
    
    await asyncio.sleep(2)
    await status_message.edit_text(
        f"⏳ *Konu:* '{topic}'\n\n✅ Senaryo yazildi.\n2. Adim: 3D Videolar uretiliyor...",
        parse_mode='Markdown'
    )
    
    await asyncio.sleep(2)
    final_text = (
        f"🎬 *VIDEON HAZIR KOMUTANIM!* 🎬\n\n"
        f"📌 *Baslik:* {topic}\n"
        f"*(Bot basariyla %100 bulutta Render uzerinde calisiyor!)*"
    )
    await status_message.edit_text(final_text, parse_mode='Markdown')

def run_bot():
    """Botu ayri bir thread icinde baslatir."""
    # Yeni bir event loop oluştur ve onu kullan
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot basliyor...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    # 1. Thread'de Telegram botunu baslat
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # 2. Ana Thread'de Flask (Web) sunucusunu baslat. Render port bekledigi icin bu sart.
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
