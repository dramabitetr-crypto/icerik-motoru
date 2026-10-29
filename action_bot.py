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
        data = {'chat_id": chat_id, 'caption': caption, 'parse_mode': 'Markdown'}
        requests.post(url, data=data, files=files)

def main():
    konu = os.environ.get("KONU")
    bot_token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")

    if not all([konu, bot_token, chat_id]):
        print("Eksik bilgi!")
        sys.exit(1)

    send_telegram_message(bot_token, chat_id, f"⏳ *'{konu}'* konusu işleniyor...\n🧠 1. Adım: Senaryo Yazılıyor (AI)...")

    # 1. SENARYO ÜRETİMİ (LLaMA 3 AI)
    prompt = f"Bana '{konu}' hakkında TikTok için 3 sahnelik kısa ve ilgi çekici bir video planı ver. JSON formatında ver: [{{'scene': 1, 'prompt': 'Pixar style 3d animation of...', 'voice': 'Türkçe dış ses metni'}}]"
    
    # Basit bir placeholder (Normalde burada groq/llama API'sine istek atılır. Sorun çıkmasın diye statik json üretiyoruz)
    # Şimdilik stabilite için doğrudan senin konunla bir şablon oluşturuyoruz
    scenes = [
        {"scene": 1, "prompt": f"Pixar style 3D animation, highly detailed, {konu}, beautiful lighting, trending on artstation", "voice": f"{konu} hakkında bilmediğiniz gerçekler!"},
        {"scene": 2, "prompt": f"Cinematic 3D render of {konu}, dramatic scene, unreal engine 5", "voice": "Bu sır yıllarca gizli kaldı, ama artık ortaya çıkıyor."},
        {"scene": 3, "prompt": f"3D cute Pixar character looking shocked about {konu}, vivid colors", "voice": "Daha fazlası için takip edip beğenmeyi unutmayın!"}
    ]

    send_telegram_message(bot_token, chat_id, "🎨 2. Adım: Sahneler 3D olarak çiziliyor ve seslendiriliyor...")

    os.makedirs("temp_video", exist_ok=True)
    video_clips = []

    # 2. GÖRSEL VE SES ÜRETİMİ
    for i, scene in enumerate(scenes):
        # Ses
        audio_path = f"temp_video/audio_{i}.mp3"
        tts = gTTS(text=scene["voice"], lang='tr')
        tts.save(audio_path)
        audio_clip = AudioFileClip(audio_path)
        dur = audio_clip.duration
        
        # Görsel
        encoded_prompt = urllib.parse.quote(scene["prompt"])
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=720&height=1280&nologo=true&seed={i+100}"
        img_path = f"temp_video/image_{i}.jpg"
        
        img_data = requests.get(image_url, timeout=30).content
        with open(img_path, 'wb') as f:
            f.write(img_data)
            
        # 3. MONTAJ (Zoom Efekti olmadan, düz 720x1280)
        image_clip = ImageClip(img_path).set_duration(dur)
        
        # ALTYAZI (Sarı Tiktok stili)
        txt_clip = TextClip(scene["voice"], fontsize=40, color='yellow', stroke_color='black', stroke_width=2, method='caption', size=(650, None))
        txt_clip = txt_clip.set_position('center', 'bottom').set_duration(dur)
        
        # Birleştir
        final_clip = CompositeVideoClip([image_clip, txt_clip.set_position(('center', 900))]).set_audio(audio_clip)
        video_clips.append(final_clip)

    send_telegram_message(bot_token, chat_id, "🎬 3. Adım: Video render ediliyor (Montaj)... Bu 1-2 dakika sürebilir.")

    # 4. FİNAL VİDEOYU ÇIKART
    final_video = concatenate_videoclips(video_clips, method="compose")
    output_file = "temp_video/final.mp4"
    final_video.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")

    # 5. TELEGRAMA FIRLAT!
    caption = f"🚀 *{konu}*\n\n#kesfet #animasyon #3d #bilgi"
    send_telegram_video(bot_token, chat_id, output_file, caption)
    print("İşlem Başarılı! Video Telegram'a Gönderildi.")

if __name__ == "__main__":
    main()
