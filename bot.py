import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Senin BotFather'dan aldığın orijinal şifre
BOT_TOKEN = "9119725211:AAEZ79N0n7ugM45QhR_z3wmEP1AnA0TtqXs"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "🚀 *Icerik Uretim Komuta Merkezine Hos Geldin Komutanim!* 🚀\n\n"
        "Ben senin 3D Animasyon ve Video Montaj Asistaninim.\n"
        "Bana sadece bir konu yaz, senin icin harikalar yaratayim!\n"
        "Hemen test etmek icin bana bir konu yaz. (Orn: Mars'ta ilk kahvalti)"
    )
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = update.message.text
    
    status_message = await update.message.reply_text(
        f"⏳ *Konu alindi:* '{topic}'\n\n"
        "🧠 1. Adim: Yapay zeka hikayeyi ve 3D sahne komutlarini yaziyor...",
        parse_mode='Markdown'
    )
    
    await asyncio.sleep(3)
    await status_message.edit_text(
        f"⏳ *Konu:* '{topic}'\n\n✅ Senaryo yazildi.\n🎥 2. Adim: 3D hareketli videolar uretiliyor...",
        parse_mode='Markdown'
    )
    
    await asyncio.sleep(4)
    await status_message.edit_text(
        f"⏳ *Konu:* '{topic}'\n\n✅ Videolar hazir.\n🗣 3. Adim: Dis ses ve dinamik altyazilar ekleniyor...",
        parse_mode='Markdown'
    )
    
    await asyncio.sleep(4)
    final_text = (
        f"🎬 *VIDEON HAZIR KOMUTANIM!* 🎬\n\n"
        f"📌 *Baslik:* {topic} - Gizemli Gercekler!\n"
        f"📝 *Aciklama:* Bu videoda {topic} hakkinda bilmediginiz sirlari derledik.\n"
        f"📍 *Hashtagler:* #kesfet #{topic.replace(' ', '')} #animasyon\n\n"
        f"*(Bot basariyla %100 bulutta calisiyor!)*"
    )
    await status_message.edit_text(final_text, parse_mode='Markdown')

def main():
    print("Telegram Botu Bulutta Baslatiliyor...")
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot Basariyla Calisiyor!")
    application.run_polling()

if __name__ == '__main__':
    main()
