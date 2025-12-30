import streamlit as st
import os
import time
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import re

# --- 1. الاستدعاء الصحيح لـ MoviePy 2.0+ (حل الـ ImportError) ---
from moviepy.video.VideoClip import ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.config import configure

# إعداد محرك الصور (ImageMagick) للسيرفر
try:
    if os.name == 'posix': # نظام لينكس (الموقع)
        configure(IMAGEMAGICK_BINARY="convert")
    else: # نظام ويندوز (جهازك)
        IMAGEMAGICK_EXE = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
        if os.path.exists(IMAGEMAGICK_EXE):
            configure(IMAGEMAGICK_BINARY=IMAGEMAGICK_EXE)
except Exception as e:
    st.warning(f"تنبيه المحرك: {e}")

try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except:
    pass

# --- 2. إعداد المسارات المؤقتة ---
BASE_PATH = os.getcwd()
MEDIA_DIR = os.path.join(BASE_PATH, "Mediawy_Studio")
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]:
    os.makedirs(d, exist_ok=True)

# --- 3. محرك الرسم (ثبات العناصر) ---
def process_static_layer(size, logo_path, marquee_text):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("arial.ttf", size[1] // 25)
    except: font = ImageFont.load_default()
    
    if marquee_text:
        draw.rectangle([0, size[1]-80, size[0], size[1]], fill=(0,0,0,180))
        draw.text((40, size[1]-65), marquee_text, font=font, fill="white")
    
    if logo_path:
        logo = Image.open(logo_path).convert("RGBA").resize((size[0]//6, size[0]//6))
        img.paste(logo, (size[0] - size[0]//6 - 30, 30), logo)
    return ImageClip(np.array(img))

def create_text_clip(size, text, start_t, dur):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("arial.ttf", size[1] // 15)
    except: font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.rectangle([size[0]//2 - tw//2 - 20, size[1]//2 - th//2 - 10, 
                    size[0]//2 + tw//2 + 20, size[1]//2 + th//2 + 10], fill=(0,0,0,160))
    draw.text((size[0]//2 - tw//2, size[1]//2 - th//2), text, font=font, fill="yellow")
    # استخدام with_start و with_duration للأصدار الجديد
    return ImageClip(np.array(img)).with_start(start_t).with_duration(dur).with_position('center')

# --- 4. واجهة المستخدم ---
st.set_page_config(page_title="Mediawy Pro V20", layout="wide")
st.title("🎬 Mediawy Studio V20 - The Master Fix")

with st.sidebar:
    st.header("⚙️ مركز التحكم")
    dim = st.selectbox("📏 الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    ai_text = st.text_area("أدخل النص هنا:", height=200)
    user_imgs = st.file_uploader("ارفع صورك (اختياري)", accept_multiple_files=True)
    marquee_text = st.text_input("نص البنر السفلي:", "Mediawy Studio 2026")
    logo_file = st.file_uploader("ارفع اللوجو الثابت")

# --- 5. محرك الإنتاج ---
if st.button("إطلاق خط الإنتاج 🚀", use_container_width=True):
    if not ai_text or not logo_file:
        st.error("⚠️ يرجى إدخال النص ورفع اللوجو!")
    else:
        status = st.empty()
        try:
            status.info("🎙️ جاري تجهيز الصوت...")
            audio_p = os.path.join(ASSETS_DIR, "v.mp3")
            gTTS(ai_text, lang='ar').save(audio_p)
            voice_clip = AudioFileClip(audio_p)
            total_dur = voice_clip.duration

            # تحليل الجمل للمزامنة
            sentences = [s.strip() for s in re.split(r'[.؟!،,]+', ai_text) if len(s.strip()) > 2]
            num_clips = len(sentences)
            dur_per_clip = total_dur / num_clips if num_clips > 0 else total_dur

            h = 1080; w = int(h*9/16) if "9:16" in dim else int(h*16/9)
            img_clips = []
            sub_clips = []

            for i, sentence in enumerate(sentences):
                p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
                if user_imgs:
                    with open(p, "wb") as fo: fo.write(user_imgs[i % len(user_imgs)].getbuffer())
                else:
                    # سحب صورة سياقية بسيطة
                    img_data = requests.get(f"https://images.unsplash.com/photo-1500000000000?w={w}&h={h}&q=80").content
                    with open(p, "wb") as fo: fo.write(img_data)
                
                # استخدامresized و with_duration للنسخة الجديدة
                c = ImageClip(p).with_duration(dur_per_clip).resized(height=h)
                img_clips.append(c)
                sub_clips.append(create_text_clip((w, h), sentence, i*dur_per_clip, dur_per_clip))

            video_track = concatenate_videoclips(img_clips, method="compose")
            
            l_p = os.path.join(ASSETS_DIR, "l.png")
            with open(l_p, "wb") as f: f.write(logo_file.getbuffer())
            static_layer = process_static_layer((w, h), l_p, marquee_text).with_duration(total_dur)

            # تجميع كل الطبقات
            final_vid = CompositeVideoClip([video_track, static_layer] + sub_clips, size=(w, h)).with_audio(voice_clip)
            
            out_p = os.path.join(VIDEOS_DIR, "Mediawy_Cloud_V20.mp4")
            final_vid.write_videofile(out_p, fps=24, codec="libx264")
            
            st.video(out_p)
            st.success("🔥 مبروك! المكنة دارت أونلاين بكامل عتادها.")
            
        except Exception as e:
            st.error(f"⚠️ خطأ أثناء الإنتاج: {str(e)}")
