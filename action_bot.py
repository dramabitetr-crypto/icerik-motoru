import os
import requests
import sys

def main():
    konu = os.environ.get("KONU")
    bot_token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")

    if not all([konu, bot_token, chat_id]):
        print("Hata: Çevresel değişkenler eksik!")
        sys.exit(1)

    print(f"Hedef Konu: {konu}")
    print("Sistem çalışıyor...")

    telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": f"🎬 *YENİ VİDEO EMRİ ALINDI!*\n\n📌 *Konu:* {konu}\n📝 GitHub Actions çalışıyor. Video motoru devreye giriyor...",
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(telegram_url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Mesaj Telegram'a başarıyla iletildi!")
    except Exception as e:
        print(f"❌ Telegram Hatası: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
