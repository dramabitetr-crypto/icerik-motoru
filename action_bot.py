import os
import sys
import requests
import json
import time
import asyncio
import edge_tts
import urllib.parse
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip

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

# Fal.ai API çağrısı yapan fonksiyon (Minimax Modeli)
def generate_video_fal(prompt, api_key):
    url = "https://queue.fal.run/fal-ai/minimax-video"
    headers = {
        "Authorization": f"Key {api_key}",
        "Content-Type": "application/json"
    }
    payload = {"prompt": prompt}
    
    print("Video API isteği atılıyor...")
    res = requests.post(url, headers=headers, json=payload)
    res.raise_for_status()
    
    request_id = res.json().get("request_id")
    print(f"İşlem sıraya alındı. ID: {request_id}")
    
    status_url = f"https://queue.fal.run/fal-ai/minimax-video/requests/{request_id}"
    
    while True:
        status_res = requests.get(status_url, headers=headers)
        status_json = status_res.json()
        status = status_json.get("status")
        
        if status == "COMPLETED":
            return status_json["video"]["url"]
        elif status == "FAILED":
            raise Exception("Video Üretimi Çöktü!")
        
        print("Video render ediliyor... Lütfen bekleyin (10s)")
        time.sleep(10)

# Asenkron ses üretme fonksiyonu (Edge TTS)
async def generate_audio(text, output_path):
    communicate = edge_tts.Communicate(text, "tr-TR-AhmetNeural", rate="+5%") 
    await communicate.save(output_path)

def main():
    konu = os.environ.get("KONU")
    bot_token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")
    fal_key = os.environ.get("FAL_KEY")

    if not all([konu, bot_token, chat_id, fal_key]):
        print("Eksik bilgi! API anahtarı veya Chat ID bulunamadı.")
        sys.exit(1)

    send_telegram_message(bot_token, chat_id, f"⏳ *'{konu}'* konusu işleniyor...\n🧠 1. Adım: Senaryo Yazılıyor ve Minimax API başlatılıyor...")

    # Animasyon sahneleri (Fal.ai / Minimax komutlarıyla)
    scenes = [
        {"scene": 1, "prompt": f"Cinematic 3d animation, {konu}, high action, moving camera, unreal engine 5 style", "voice": f"{konu} hakkında inanılmaz bir yolculuğa başlıyoruz!"},
        {"scene": 2, "prompt": f"Close up 3d animation character reacting to {konu}, funny and expressive, motion blur", "voice": "Bazı şeyler gerçekten çok hızlı değişiyor."},
    ]

    send_telegram_message(bot_token, chat_id, "🎥 2. Adım: Hareketli 3D Videolar Üretiliyor... (Minimax motoru devrede. Bu işlem 2-3 dakika sürebilir)")

    os.makedirs("temp_video", exist_ok=True)
    video_clips = []

    for i, scene in enumerate(scenes):
        try:
            # 1. Sesi oluştur
            audio_path = f"temp_video/audio_{i}.mp3"
            asyncio.run(generate_audio(scene["voice"], audio_path))
            
            audio_clip = AudioFileClip(audio_path)
            dur = audio_clip.duration
            
            # 2. Hareketli videoyu Fal.ai ile oluştur
            video_url = generate_video_fal(scene["prompt"], fal_key)
            print(f"Sahne {i+1} videosu alındı: {video_url}")
            
            vid_path = f"temp_video/scene_{i}.mp4"
            vid_data = requests.get(video_url).content
            with open(vid_path, 'wb') as f:
                f.write(vid_data)
                
            # 3. Kurgu: Animasyonlu video ve sesi birleştir
            base_clip = VideoFileClip(vid_path).subclip(0, min(dur, 5)) 
            
            # 4. Altyazıyı Ekle (Tiktok formatı)
            txt_clip = TextClip(scene["voice"], fontsize=45, color='yellow', stroke_color='black', stroke_width=2, method='caption', size=(650, None))
            txt_clip = txt_clip.set_position('center', 'bottom').set_duration(base_clip.duration)
            
            final_clip = CompositeVideoClip([base_clip, txt_clip.set_position(('center', 900))]).set_audio(audio_clip)
            video_clips.append(final_clip)
            
        except Exception as e:
            print(f"HATA: Sahne {i+1} atlandı: {e}")
            send_telegram_message(bot_token, chat_id, f"⚠️ Sahne {i+1} üretilirken hata oluştu.")

    if not video_clips:
        send_telegram_message(bot_token, chat_id, "❌ Hiçbir sahne üretilemedi.")
        sys.exit(1)

    send_telegram_message(bot_token, chat_id, "🎬 3. Adım: Video sesler ve altyazıyla montajlanıyor...")

    # Final Videoyu çıkart
    final_video = concatenate_videoclips(video_clips, method="compose")
    output_file = "temp_video/final.mp4"
    final_video.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")

    # Telegram'a fırlat
    caption = f"🚀 *{konu}*\n\n#kesfet #animasyon #3d #bilgi"
    send_telegram_video(bot_token, chat_id, output_file, caption)
    print("İşlem Başarılı! 3D Animasyon Videosu Telegram'a Gönderildi.")

if __name__ == "__main__":
    main()
