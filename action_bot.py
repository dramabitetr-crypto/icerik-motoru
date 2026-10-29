import os
import sys
import requests
import urllib.parse
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
from gradio_client import Client

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

# API anahtarı istemeyen sınırsız Gradio (Hugging Face) Bot Motoru
def generate_free_image(prompt):
    print(f"Hugging Face (Gradio) uzerinden ucretsiz resim cizdiriliyor: {prompt}")
    try:
        # Sınırsız ve ücretsiz açık kaynaklı model (SDXL)
        client = Client("stabilityai/stable-diffusion-3-medium")
        result = client.predict(
            prompt=prompt,
            negative_prompt="ugly, deformed, blurry, text, watermark",
            seed=0,
            randomize_seed=True,
            width=768,
            height=1024,
            guidance_scale=5,
            num_inference_steps=28,
            api_name="/infer"
        )
        # Result, indirilen dosyanin yolunu (path) doner
        image_path = result[0] 
        return image_path
    except Exception as e:
        print(f"Hugging Face uretiminde hata: {e}")
        return None

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
        {"scene": 1, "prompt": f"Cinematic 3D animation, highly detailed, {konu}, beautiful lighting, unreal engine 5", "voice": f"{konu} hakkında bilmediğiniz korkunç gerçekler!"},
        {"scene": 2, "prompt": f"Close up 3D character reacting to {konu}, vivid colors, movie still", "voice": "Bu sır yıllarca gizli kaldı, ama artık yüzleşme vakti geldi."},
        {"scene": 3, "prompt": f"Epic wide shot of {konu}, dramatic scene, 8k resolution", "voice": "Daha fazlası için takip edip beğenmeyi unutmayın!"}
    ]

    send_telegram_message(bot_token, chat_id, "🎨 2. Adım: Sahneler 3D olarak çiziliyor (Hugging Face kullanılıyor) ve seslendiriliyor...")

    os.makedirs("temp_video", exist_ok=True)
    video_clips = []

    for i, scene in enumerate(scenes):
        try:
            # 1. Ses oluştur
            audio_path = f"temp_video/audio_{i}.mp3"
            tts = gTTS(text=scene["voice"], lang='tr')
            tts.save(audio_path)
            audio_clip = AudioFileClip(audio_path)
            dur = audio_clip.duration
            
            # 2. ÜCRETSİZ RESİM İNDİR (Hugging Face)
            img_path = generate_free_image(scene["prompt"])
            
            if not img_path or not os.path.exists(img_path):
                raise ValueError("Resim uretilemedi.")
                
            # 3. KAMERA EFEKTİ VE MONTAJ 
            image_clip = ImageClip(img_path).set_duration(dur)
            moving_image = image_clip.resize(lambda t: zoom_in_effect(t, dur)).crop(x_center=384, y_center=512, width=720, height=1024)
            
            # 4. ALTYAZI (Sarı Tiktok stili)
            txt_clip = TextClip(scene["voice"], fontsize=45, color='yellow', stroke_color='black', stroke_width=2, method='caption', size=(650, None))
            txt_clip = txt_clip.set_position('center', 'bottom').set_duration(dur)
            
            final_clip = CompositeVideoClip([moving_image, txt_clip.set_position(('center', 800))]).set_audio(audio_clip)
            video_clips.append(final_clip)
            
        except Exception as e:
            print(f"HATA: Sahne {i+1} atlandı: {e}")
            send_telegram_message(bot_token, chat_id, f"⚠️ Sahne {i+1} üretilirken hata oluştu.")

    if not video_clips:
        send_telegram_message(bot_token, chat_id, "❌ Hiçbir sahne üretilemedi.")
        sys.exit(1)

    send_telegram_message(bot_token, chat_id, "🎬 3. Adım: Video efektler ve altyazıyla montajlanıyor... (Bu işlem 2 dakika sürebilir)")

    final_video = concatenate_videoclips(video_clips, method="compose")
    output_file = "temp_video/final.mp4"
    final_video.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")

    caption = f"🚀 *{konu}*\n\n#kesfet #animasyon #3d #bilgi"
    send_telegram_video(bot_token, chat_id, output_file, caption)
    print("İşlem Başarılı! Video Telegram'a Gönderildi.")

if __name__ == "__main__":
    main()
