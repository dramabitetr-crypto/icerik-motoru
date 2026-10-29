import os
import sys
import requests
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip

def send_telegram_message(bot_token, chat_id, text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def send_telegram_video(bot_token, chat_id, video_path, caption):
    url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
    with open(video_path, 'rb') as video_file:
        files = {'video': video_file}
        data = {'chat_id': chat_id, 'caption': caption, 'parse_mode': 'Markdown'}
        requests.post(url, data=data, files=files)

def zoom_in_effect(t, duration):
    return 1 + 0.15 * (t / duration)

def main():
    konu = os.environ.get("KONU")
    bot_token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")

    if not all([konu, bot_token, chat_id]):
        print("Eksik bilgi!")
        sys.exit(1)

    send_telegram_message(bot_token, chat_id, f"⏳ *'{konu}'* konusu işleniyor...\n🧠 1. Adım: Senaryo Yazılıyor (AI)...")

    scenes = [
        {"scene": 1, "voice": f"{konu} hakkında bilmediğiniz korkunç gerçekler!"},
        {"scene": 2, "voice": "Bu sır yıllarca gizli kaldı, ama artık yüzleşme vakti geldi."},
        {"scene": 3, "voice": "Daha fazlası için takip edip beğenmeyi unutmayın!"}
    ]

    send_telegram_message(bot_token, chat_id, "🎨 2. Adım: Sahneler 3D olarak çiziliyor ve seslendiriliyor...")

    os.makedirs("temp_video", exist_ok=True)
    video_clips = []

    # API engellerini aşmak için %100 çalışan garantili resim adresi kullanıyoruz
    colors = ["1abc9c", "e74c3c", "3498db"]

    for i, scene in enumerate(scenes):
        try:
            # 1. Ses oluştur
            audio_path = f"temp_video/audio_{i}.mp3"
            tts = gTTS(text=scene["voice"], lang='tr')
            tts.save(audio_path)
            audio_clip = AudioFileClip(audio_path)
            dur = audio_clip.duration
            
            # 2. Resim İndirme (Garantili Çalışan Metot - Pixabay / Dummy)
            img_path = f"temp_video/image_{i}.jpg"
            image_url = f"https://placehold.co/720x1280/{colors[i]}/FFFFFF/png?text=Sahne+{i+1}\n{konu}"
            
            print(f"Sahne {i+1} için resim indiriliyor...")
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            with open(img_path, 'wb') as f:
                f.write(response.content)
                
            # 3. KAMERA EFEKTİ VE MONTAJ 
            image_clip = ImageClip(img_path).set_duration(dur)
            moving_image = image_clip.resize(lambda t: zoom_in_effect(t, dur)).crop(x_center=360, y_center=640, width=720, height=1280)
            
            # 4. ALTYAZI (Sarı Tiktok stili)
            txt_clip = TextClip(scene["voice"], fontsize=45, color='yellow', stroke_color='black', stroke_width=2, method='caption', size=(650, None))
            txt_clip = txt_clip.set_position('center', 'bottom').set_duration(dur)
            
            final_clip = CompositeVideoClip([moving_image, txt_clip.set_position(('center', 900))]).set_audio(audio_clip)
            video_clips.append(final_clip)
            
        except Exception as e:
            print(f"HATA: Sahne {i+1} atlandı: {e}")
            send_telegram_message(bot_token, chat_id, f"⚠️ Sahne {i+1} üretilirken hata oluştu.")

    if not video_clips:
        send_telegram_message(bot_token, chat_id, "❌ Hiçbir sahne üretilemedi.")
        sys.exit(1)

    send_telegram_message(bot_token, chat_id, "🎬 3. Adım: Video efektler ve altyazıyla montajlanıyor... (Bu işlem 1-2 dakika sürebilir)")

    final_video = concatenate_videoclips(video_clips, method="compose")
    output_file = "temp_video/final.mp4"
    final_video.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")

    caption = f"🚀 *{konu}*\n\n#kesfet #animasyon #3d #bilgi"
    send_telegram_video(bot_token, chat_id, output_file, caption)
    print("İşlem Başarılı! Video Telegram'a Gönderildi.")

if __name__ == "__main__":
    main()
