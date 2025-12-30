import streamlit as st
import os
import time
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import re

# --- 1. التعديل الذهبي للموقع (تأمين المحركات أونلاين) ---
from moviepy.config import change_settings

# هذا السطر هو مفتاح الحل على Streamlit Cloud (Linux)
try:
    if os.name == 'posix':  # نظام لينكس (الموقع)
        change_settings({"IMAGEMAGICK_BINARY": "convert"})
    else:  # نظام ويندوز (جهازك الشخصي)
        IMAGEMAGICK_EXE = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
        if os.path.exists(IMAGEMAGICK_EXE):
            change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_EXE})
except Exception as e:
    st.warning(f"تنبيه محرك الصور: {e}")

try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except:
    pass

from moviepy.editor import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip

# --- 2. إعداد المجلدات المؤقتة بالسيرفر ---
BASE_PATH = os.getcwd()
MEDIA_DIR = os.path.join(BASE_PATH, "Mediawy_Studio")
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- 3. محرك الرسم (ثبات اللوجو والبنر والنص) ---
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

def create_text_clip(size, text, start_t, end_t):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("arial.ttf", size[1] // 15)
    except: font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.rectangle([size[0]//2 - tw//2 - 20, size[1]//2 - th//2 - 10, 
                    size[0]//2 + tw//2 + 20, size[1]//2 + th//2 + 10], fill=(0,0,0,160))
    draw.text((size[0]//2 - tw//2, size[1]//2 - th//2), text, font=font, fill="yellow")
    return ImageClip(np.array(img)).set_start(start_t).set_end(end_t).set_position('center')

# --- 4. واجهة المستخدم ---
st.set_page_config(page_title="Mediawy Pro V16", layout="wide")
st.markdown("<h1 style='text-align:center; color:#e60000;'>Mediawy Studio <span style='color:#00e5ff;'>Cloud V16</span></h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ مركز التحكم")
    dim = st.selectbox("📏 الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    edit_style = st.selectbox("🎭 النمط:", ["سينمائي", "درامي", "وثائقي"])
    st.markdown("---")
    ai_text = st.text_area("النص (حتى 500 كلمة):", height=150)
    bg_music_opt = st.toggle("🎵 موسيقى + Ducking", value=True)
    ducking_strength = st.slider("🔇 خفض الموسيقى:", 0.05, 0.4, 0.1)
    st.markdown("---")
    img_mode = st.radio("🖼️ الصور:", ["سياق أوتوماتيك AI", "يدوي (بشرى)"])
    user_imgs = st.file_uploader("ارفع صورك", accept_multiple_files=True)
    marquee_text = st.text_input("🎞️ نص البنر:", "Mediawy Studio 2025")
    logo_file = st.file_uploader("🚩 ارفع اللوجو")

# --- 5. محرك الإنتاج ---
if st.button("إطلاق خط الإنتاج 🚀", use_container_width=True):
    if not ai_text or not logo_file:
        st.error("⚠️ يرجى التأكد من النص واللوجو!")
    else:
        status = st.empty()
        try:
            status.info("🎙️ جاري تجهيز الصوت والسياق...")
            audio_p = os.path.join(ASSETS_DIR, "v.mp3")
            gTTS(ai_text, lang='ar').save(audio_p)
            voice_clip = AudioFileClip(audio_p)
            total_dur = voice_clip.duration

            # تقسيم السياق
            sentences = re.split(r'[.؟!،,]+', ai_text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 3]
            num_clips = len(sentences)
            dur_per_clip = total_dur / num_clips

            h = 10
