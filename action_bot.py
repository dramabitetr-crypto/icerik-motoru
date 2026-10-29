import os
import sys
import requests
import json
import time
from gtts import gTTS
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

def generate_video_fal(prompt, api_key):
    url = "https://queue.fal.run/fal-ai/minimax-video"
    headers = {
        "Authorization": f"Key {api_key}",
        "Content-Type": "application/json"
    }
    payload = {"prompt": prompt}
    
    print("Video API istegi atiliyor...")
    res = requests.post(url, headers=headers, json=payload)
    res.raise_for_status()
    
    request_id = res.json().get("request_id")
    print(f"Islem siraya alindi. ID: {request_id}")
    
    status_url = f"https://queue.fal.run/fal-ai/minimax-video/requests/{request_id}"
    
    while True:
        status_res = requests.get(status_url, headers=headers)
        status_json = status_res.json()
        status = status_json.get("status")
        
        if status == "COMPLETED":
            return status_json["video"]["url"]
        elif status == "FAILED":
            raise Exception("Video Uretimi Coktu!")
        
        print("Video render ediliyor... Lutfen bekleyin (10s)")
        time.sleep(10)

def main():
    konu = os.environ.get("KONU")
    bot_token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")
    fal_key = os.environ.get("FAL_KEY")

    if not all([konu, bot_token, chat_id, fal_key]):
        print("Eksik bilgi!")
        sys.exit(1)

    send_telegram_message(bot_token, chat_id, f"⏳ *'{konu}'* konusu isleniyor...\n🧠 1. Adim: Senaryo Yaziliyor ve Minimax API baslatiliyor...")

    scenes = [
        {"scene": 1, "prompt": f"Cinematic 3d animation, {konu}, high action, moving camera, unreal engine 5 style", "voice": f"{konu} hakkinda inanilmaz bir yolculuga basliyoruz!"},
        {"scene": 2, "prompt": f"Close up 3d animation character reacting to {konu}, funny and expressive, motion blur", "voice": "Bazi seyler gercekten cok hizli degisiyor."},
    ]

    send_telegram_message(bot_token, chat_id, "🎥 2. Adim: Hareketli 3D Videolar Uretiliyor... (Minimax motoru devrede. Bu islem 2-3 dakika surebilir)")

    os.makedirs("temp_video", exist_ok=True)
    video_clips = []

    for i, scene in enumerate(scenes):
        try:
            audio_path = f"temp_video/audio_{i}.mp3"
            tts = gTTS(text=scene["voice"], lang='tr')
            tts.save(audio_path)
            audio_clip = AudioFileClip(audio_path)
            dur = audio_clip.duration
            
            video_url = generate_video_fal(scene["prompt"], fal_key)
            print(f"Sahne {i+1} videousu alindi: {video_url}")
            
            vid_path = f"temp_video/scene_{i}.mp4"
            vid_data = requests.get(video_url).content
            with open(vid_path, 'wb') as f:
                f.write(vid_data)
                
            base_clip = VideoFileClip(vid_path).subclip(0, min(dur, 5))
            
            txt_clip = TextClip(scene["voice"], fontsize=45, color='yellow', stroke_color='black', stroke_width=2, method='caption', size=(650, None))
            txt_clip = txt_clip.set_position('center', 'bottom').set_duration(base_clip.duration)
            
            final_clip = CompositeVideoClip([base_clip, txt_clip.set_position(('center', 900))]).set_audio(audio_clip)
            video_clips.append(final_clip)
            
        except Exception as e:
            print(f"HATA: Sahne {i+1} atlandi: {e}")
            send_telegram_message(bot_token, chat_id, f"⚠️ Sahne {i+1} uretilirken hata olustu.")

    if not video_clips:
        send_telegram_message(bot_token, chat_id, "❌ Hicbir sahne uretilemedi.")
        sys.exit(1)

    send_telegram_message(bot_token, chat_id, "🎬 3. Adim: Video sesler ve altyaziyla montajlaniyor...")

    final_video = concatenate_videoclips(video_clips, method="compose")
    output_file = "temp_video/final.mp4"
    final_video.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")

    caption = f"🚀 *{konu}*\n\n#kesfet #animasyon #3d #bilgi"
    send_telegram_video(bot_token, chat_id, output_file, caption)
    print("Islem Basarili! 3D Animasyon Videosu Telegram'a Gonderildi.")

if __name__ == "__main__":
    main()
