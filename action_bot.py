import os
import sys
import requests
import urllib.parse
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

# Levent'in tarzına uygun hafif Zoom-in efekti (Dinamizm katar)
def zoom_in_effect(t, duration):
    return 1 + 0.15 * (t / duration)

def main():
    konu = os.environ.get("KONU")
    bot_token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")

    if not all([konu, bot_token, chat_id]):
        print("Eksik bilgi! Çevresel değişkenler bulunamadı.")
        sys.exit(1)

    send_telegram_message(bot_token, chat_id, f"🎬 *LEVENT MOTORU ÇALIŞIYOR!*\n\n📌 *Konu:* {konu}\n🧠 1. Adım: Levent'in komik senaryosu yazılıyor...")

    # Levent'in sabit mizahi yapısına uygun şablon sahneler
    scenes = [
        {"scene": 1, "prompt": f"3d pixar style animation, a handsome friendly man named Levent, talking excitedly about {konu}, highly detailed, unreal engine", "voice": f"Bunu duyunca şok olacaksınız! {konu} hakkında inanılmaz bir şey buldum!"},
        {"scene": 2, "prompt": f"3d pixar style animation, same man Levent looking confused and funny, reacting to {konu}, vivid colors", "voice": "Önce saçma geldi, ama işin aslı hiç de öyle değilmiş."},
        {"scene": 3, "prompt": f"3d pixar style animation, same man Levent smiling and pointing at camera, {konu} in background", "voice": "Abone olmayı ve videoyu kaydetmeyi unutmayın!"}
    ]

    send_telegram_message(bot_token, chat_id, "🎨 2. Adım: Levent'in sahneleri çiziliyor ve seslendiriliyor...")

    os.makedirs("temp_video", exist_ok=True)
    video_clips = []
    
    colors = ["1abc9c", "e74c3c", "3498db"] # Hata olursa devreye girecek acil durum arkaplanları

    for i, scene in enumerate(scenes):
        try:
            # 1. Ses oluştur (Geçici Google Sesi, sonra Levent'in orijinal sesini bağlayacağız)
            audio_path = f"temp_video/audio_{i}.mp3"
            tts = gTTS(text=scene["voice"], lang='tr')
            tts.save(audio_path)
            audio_clip = AudioFileClip(audio_path)
            dur = audio_clip.duration
            
            # 2. ÜCRETSİZ RESİM İNDİR (Pollinations AI - Sınırsız)
            img_path = f"temp_video/image_{i}.jpg"
            encoded_prompt = urllib.parse.quote(scene["prompt"])
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=720&height=1280&nologo=true&seed={i+5000}"
            
            print(f"Sahne {i+1} için resim indiriliyor...")
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            with open(img_path, 'wb') as f:
                f.write(response.content)
                
            # Güvenlik duvarı (bozuk resim engeli)
            if os.path.getsize(img_path) < 10000:
                raise ValueError("Sunucu bozuk resim yolladı.")
                
        except Exception as e:
            print(f"HATA: Sahne {i+1} resmi indirilemedi: {e}. Acil durum arkaplanı kullanılıyor.")
            dummy_url = f"https://placehold.co/720x1280/{colors[i]}/FFFFFF/png?text=Levent+Sahne+{i+1}"
            img_data = requests.get(dummy_url).content
            with open(img_path, 'wb') as f:
                f.write(img_data)
                
        # 3. KAMERA EFEKTİ VE MONTAJ (Görüntüye hareket kat)
        image_clip = ImageClip(img_path).set_duration(dur)
        moving_image = image_clip.resize(lambda t: zoom_in_effect(t, dur)).crop(x_center=360, y_center=640, width=720, height=1280)
        
        # 4. DİNAMİK TİKTOK ALTYAZISI (Ekrana vuran sarı yazılar)
        txt_clip = TextClip(scene["voice"], fontsize=45, color='yellow', stroke_color='black', stroke_width=2, method='caption', size=(650, None))
        txt_clip = txt_clip.set_position('center', 'bottom').set_duration(dur)
        
        final_clip = CompositeVideoClip([moving_image, txt_clip.set_position(('center', 900))]).set_audio(audio_clip)
        video_clips.append(final_clip)

    send_telegram_message(bot_token, chat_id, "🎬 3. Adım: Levent'in videosu montajlanıyor... (Lütfen 1-2 dakika bekleyin)")

    # 4. FİNAL VİDEOYU ÇIKART VE TELEGRAMA AT
    final_video = concatenate_videoclips(video_clips, method="compose")
    output_file = "temp_video/levent_final.mp4"
    final_video.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")

    caption = f"🚀 *LEVENT SUNAR: {konu}*\n\n#kesfet #komedi #animasyon #bilgi"
    send_telegram_video(bot_token, chat_id, output_file, caption)
    print("İşlem Başarılı! Levent'in ilk videosu Telegram'a Gönderildi.")

if __name__ == "__main__":
    main()
