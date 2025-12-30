import streamlit as st
import os
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import re

# --- 1. الاستدعاء الشامل والمستقر لـ MoviePy 2.x ---
# بننادي المكتبة الأم، وهي اللي بتوزع المهام داخلياً لمنع أخطاء المسارات
import moviepy as mp
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip

# ضبط المحرك يدوياً (أكثر الطرق استقراراً أونلاين)
if os.name == 'posix': # سيرفر لينكس (الموقع)
    os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"
else: # ويندوز (جهازك)
    magick_path = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
    if os.path.exists(magick_path):
        os.environ["IMAGEMAGICK_BINARY"] = magick_path

# --- 2. إعداد المجلدات المؤقتة ---
BASE_PATH = os.getcwd()
MEDIA_DIR = os.path.join(BASE_PATH, "Mediawy_Studio")
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: 
    os.makedirs(d, exist_ok=True)

# --- 3. محرك الرسم (ثبات اللوجو والبنر) ---
def create_static_layer(size, logo_path, marquee_text):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("arial.ttf", size[1] // 25)
    except: font = ImageFont.load_default()
    
    if marquee_text:
        # رسم مستطيل خلفية البنر
        draw.rectangle([0, size[1]-80, size[0], size[1]], fill=(0,0,0,180))
        draw.text((40, size[1]-65), marquee_text, font=font, fill="white")
    
    if logo_path:
        logo = Image.open(logo_path).convert("RGBA").resize((size[0]//6, size[0]//6))
        img.paste(logo, (size[0]-size[0]//6-30, 30), logo)
    return ImageClip(np.array(img))

def create_text_clip(size, text, start_t, dur):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("arial.ttf", size[1] // 15)
    except: font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    draw.rectangle([size[0]//2-tw//2-20, size[1]//2-th//2-10, 
                    size[0]//2+tw//2+20, size[1]//2+th//2+10], fill=(0,0,0,160))
    draw.text((size[0]//2-tw//2, size[1]//2-th//2), text, font=font, fill="yellow")
    
    # استخدام أوامر MoviePy 2.x الحديثة
    return ImageClip(np.array(img)).with_start(start_t).with_duration(dur).with_position('center')

# --- 4. واجهة المستخدم ---
st.set_page_config(page_title="Mediawy Pro V26", layout="wide")
st.title("🎬 Mediawy Studio V26 - Universal Setup")

with st.sidebar:
    st.header("⚙️ مركز التحكم")
    dim = st.selectbox("📏 الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    ai_text = st.text_area("أدخل النص هنا:", height=150)
    user_imgs = st.file_uploader("ارفع صورك", accept_multiple_files=True)
    logo_file = st.file_uploader("ارفع اللوجو")

# --- 5. محرك الإنتاج ---
if st.button("إطلاق خط الإنتاج 🚀", use_container_width=True):
    if not ai_text or not logo_file:
        st.error("⚠️ من فضلك تأكد من النص ورفع اللوجو!")
    else:
        status = st.empty()
        try:
            status.info("🎙️ جاري تجهيز الصوت...")
            audio_p = os.path.join(ASSETS_DIR, "v.mp3")
            gTTS(ai_text, lang='ar').save(audio_p)
            voice_clip = AudioFileClip(audio_p)
            total_dur = voice_clip.duration

            # تقسيم النص لمزامنة الصور
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
                    # سحب صور سياقية افتراضية في حالة عدم الرفع
                    img_data = requests.get(f"https://images.unsplash.com/photo-1500000000000?w={w}&h={h}&q=80").content
                    with open(p, "wb") as fo: fo.write(img_data)
                
                # استخدامresized و with_duration للنسخة الجديدة
                c = ImageClip(p).with_duration(dur_per_clip).resized(height=h)
                img_clips.append(c)
                sub_clips.append(create_text_clip((w, h), sentence, i*dur_per_clip, dur_per_clip))

            video_track = concatenate_videoclips(img_clips, method="compose")
            
            l_p = os.path.join(ASSETS_DIR, "l.png")
            with open(l_p, "wb") as f: f.write(logo_file.getbuffer())
            static_layer = create_static_layer((w, h), l_p, "Mediawy Studio 2026").with_duration(total_dur)

            # تجميع كل الطبقات (الفيديو + اللوجو + النصوص)
            final_vid = CompositeVideoClip([video_track, static_layer] + sub_clips, size=(w, h)).with_audio(voice_clip)
            
            out_p = os.path.join(VIDEOS_DIR, "Final_Mediawy.mp4")
            final_vid.write_videofile(out_p, fps=24, codec="libx264")
            
            st.video(out_p)
            st.success("🔥 مبروك! المكنة دارت أونلاين بكفاءة.")
            
        except Exception as e:
            st.error(f"⚠️ خطأ أثناء الإنتاج: {str(e)}")
