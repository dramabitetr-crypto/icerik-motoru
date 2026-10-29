import os
import sys
import requests
import json
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

def main():
    konu = os.environ.get("KONU")
    bot_token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")

    if not all([konu, bot_token, chat_id]):
        print("Eksik bilgi!")
        sys.exit(1)

    send_telegram_message(bot_token, chat_id, f"⏳ *'{konu}'* konusu isleniyor...\n🧠 1. Adim: Senaryo Yaziliyor (AI)...")

    scenes = [
        {"scene": 1, "prompt": f"Pixar style 3D animation, highly detailed, {konu}, beautiful lighting, trending on artstation", "voice": f"{konu} hakkinda bilmediginiz gercekler!"},
        {"scene": 2, "prompt": f"Cinematic 3D render of {konu}, dramatic scene, unreal engine 5", "voice": "Bu sir yillarca gizli kaldi, ama artik ortaya cikiyor."},
        {"scene": 3, "prompt": f"3D cute Pixar character looking shocked about {konu}, vivid colors", "voice": "Daha fazlasi icin takip edip begenmeyi unutmayin!"}
    ]

    send_telegram_message(bot_token, chat_id, "🎨 2. Adim: Sahneler 3D olarak ciziliyor ve seslendiriliyor...")

    os.makedirs("temp_video", exist_ok=True)
    video_clips = []

    for i, scene in enumerate(scenes):
        # 1. Ses olustur
        audio_path = f"temp_video/audio_{i}.mp3"
        tts = gTTS(text=scene["voice"], lang='tr')
        tts.save(audio_path)
        audio_clip = AudioFileClip(audio_path)
        dur = audio_clip.duration
        
        # 2. Resim Indirme ve Hata Kontrolu
        encoded_prompt = urllib.parse.quote(scene["prompt"])
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=720&height=1280&nologo=true&seed={i+1000}"
        img_path = f"temp_video/image_{i}.jpg"
        
        try:
            print(f"Sahne {i+1} icin resim indiriliyor...")
            response = requests.get(image_url, timeout=45)
            response.raise_for_status()
            with open(img_path, 'wb') as f:
                f.write(response.content)
                
            if os.path.getsize(img_path) < 10000:
                raise ValueError("Resim boyutu cok kucuk (bozuk dosya).")
                
        except Exception as e:
            print(f"Resim indirme hatasi (Sahne {i+1}): {e}. Gecici resim kullaniliyor.")
            dummy_url = f"https://placehold.co/720x1280/2980b9/FFFFFF/png?text=Sahne+{i+1}"
            img_data = requests.get(dummy_url).content
            with open(img_path, 'wb') as f:
                f.write(img_data)
                
        # 3. Montaj
        image_clip = ImageClip(img_path).set_duration(dur)
        txt_clip = TextClip(scene["voice"], fontsize=45, color='yellow', stroke_color='black', stroke_width=2, method='caption', size=(650, None))
        txt_clip = txt_clip.set_position('center', 'bottom').set_duration(dur)
        
        final_clip = CompositeVideoClip([image_clip, txt_clip.set_position(('center', 900))]).set_audio(audio_clip)
        video_clips.append(final_clip)

    send_telegram_message(bot_token, chat_id, "🎬 3. Adim: Video render ediliyor (Montaj)... Bu 1-2 dakika surebilir.")

    # 4. Videoyu Cikart
    final_video = concatenate_videoclips(video_clips, method="compose")
    output_file = "temp_video/final.mp4"
    final_video.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")

    # 5. Telegram'a Gonder
    caption = f"🚀 *{konu}*\n\n#kesfet #animasyon #3d #bilgi"
    send_telegram_video(bot_token, chat_id, output_file, caption)
    print("Islem Basarili! Video Telegram'a Gonderildi.")

if __name__ == "__main__":
    main()
