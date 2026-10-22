import os
import requests
from flask import Flask, request, jsonify, send_file
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip

app = Flask(__name__)

TEMP_DIR = "/tmp" if os.environ.get("RENDER") else "video_temp"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# Zoom in efekti (Ken Burns)
def zoom_in_effect(t, duration):
    return 1 + 0.15 * (t / duration)

@app.route('/generate_video', methods=['POST'])
def generate_video():
    try:
        data = request.json
        scenes = data.get("scenes", [])
        if not scenes: return jsonify({"error": "Sahneler eksik!"}), 400

        video_clips = []
        for i, scene in enumerate(scenes):
            image_url = scene.get("imageUrl")
            voiceover = scene.get("voiceover")
            
            # 1. Resmi İndir
            img_path = os.path.join(TEMP_DIR, f"scene_{i}.jpg")
            img_data = requests.get(image_url).content
            with open(img_path, 'wb') as handler: handler.write(img_data)
                
            # 2. Sesi Oluştur (TTS)
            audio_path = os.path.join(TEMP_DIR, f"scene_{i}.mp3")
            tts = gTTS(text=voiceover, lang='tr')
            tts.save(audio_path)
            
            # 3. Kurgu: Resim + Ses
            audio_clip = AudioFileClip(audio_path)
            dur = audio_clip.duration
            image_clip = ImageClip(img_path).with_duration(dur)
            
            # Ken Burns Zoom Efekti
            moving_image = image_clip.resized(lambda t: zoom_in_effect(t, dur))
            cropped_image = moving_image.cropped(x_center=moving_image.w/2, y_center=moving_image.h/2, width=720, height=1280)
            
            # 4. Altyazı Ekleme (Ortaya Sarı Yazı)
            txt_clip = TextClip(text=voiceover, font="Impact", font_size=50, color='yellow', stroke_color='black', stroke_width=2, size=(600, None), method='caption')
            txt_clip = txt_clip.with_position(('center', 'center')).with_duration(dur)
            
            # Resmi, altyazıyı ve sesi birleştir
            final_scene = CompositeVideoClip([cropped_image, txt_clip]).with_audio(audio_clip)
            video_clips.append(final_scene)
            
        final_video = concatenate_videoclips(video_clips, method="compose")
        output_path = os.path.join(TEMP_DIR, "final_tiktok_video.mp4")
        final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
        
        return send_file(output_path, mimetype='video/mp4')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
