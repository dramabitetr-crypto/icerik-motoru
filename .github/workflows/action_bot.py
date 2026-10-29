import os
import requests

konu = os.environ.get("KONU")
bot_token = os.environ.get("BOT_TOKEN")
chat_id = os.environ.get("CHAT_ID")

print(f"Hedef Konu: {konu}")
print("1. Adım: Senaryo yazılıyor...")
# Burada video üretim işlemleri (API vs.) olacak...
print("2. Adım: Video üretiliyor...")
print("3. Adım: Telegram'a fırlatılıyor...")

# Telegram'a mesaj atma komutu (Şimdilik mesaj atıyor, sonra videoyu atacak)
telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
mesaj = f"🎬 *YENİ VİDEO HAZIR!*\n\n📌 *Konu:* {konu}\n📝 GitHub Actions sunucuları tarafından başarıyla üretildi."

payload = {
    "chat_id": chat_id,
    "text": mesaj,
    "parse_mode": "Markdown"
}
try:
    # Hata vermemesi için şimdilik isteği yorum satırına almadık, gerçek CHAT_ID'yi alınca aktif edeceğiz.
    requests.post(telegram_url, json=payload)
    print("Telegram'a başarıyla iletildi (veya denendi).")
except Exception as e:
    print(f"Hata: {e}")
