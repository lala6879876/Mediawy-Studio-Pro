import streamlit as st
import os, requests, re, io, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip, vfx

# 1- إعداد البيئة (11- فواصل المجلدات)
MEDIA_DIR = "Mediawy_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- 4. محرك الصيد المتعدد (أقوى نظام صور حتى الآن) ---
def get_pro_image(sentence, path, size, index):
    w, h = size
    words = re.findall(r'\w+', sentence)
    q = words[0] if words else "vision"
    
    # قائمة المصادر العالمية (نظام التبادل)
    sources = [
        f"https://api.unsplash.com/photos/random?query={q}&client_id=YOUR_ACCESS_KEY", # لو عندك API
        f"https://loremflickr.com/{w}/{h}/{q}?lock={index}",
        f"https://picsum.photos/seed/{random.randint(1,999)}/{w}/{h}",
        f"https://source.unsplash.com/featured/{w}x{h}/?{q},cinematic"
    ]
    
    for url in sources:
        try:
            # تخطي المصادر اللي محتاجة Key لو مش موجود واستخدام الباقي
            if "api.unsplash" in url: continue 
            
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                img = Image.open(io.BytesIO(resp.content)).convert("RGB").resize(size)
                img.save(path, "JPEG")
                if os.path.exists(path) and os.path.getsize(path) > 100:
                    return True
        except:
            continue

    # لو كل المواقع قفلت (حل الطوارئ الاحترافي)
    img = Image.new("RGB", size, (10, 10, 20))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, w, h], fill=(index*40%255, 30, 80))
    img.save(path, "JPEG")
    return True

# --- واجهة المستخدم (تثبيت الـ 11 إضافة) ---
st.set_page_config(page_title="Mediawy V95 Pro", layout="wide")
st.markdown("<h1 style='text-align:center; color:#00FFCC;'>🎬 Mediawy Studio V95 <span style='color:white;'>Ultimate</span></h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ مركز العمليات")
    dim = st.selectbox("📏 الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    audio_src = st.radio("🎙️ الصوت:", ["بشري 🎤", "AI 🤖"])
    u_voice = st.file_uploader("ارفع صوتك") if "بشري" in audio_src else None
    ai_text = st.text_area("✍️ النص:", value="الإبداع هو أن ترى ما لا يراه الآخرون.")
    st.divider()
    u_music = st.file_uploader("🎵 موسيقى خلفية")
    logo_file = st.file_uploader("9- اللوجو")

# --- محرك الرندر النهائي ---
if st.button("🚀 إطلاق رندر القوة القصوى (V95)"):
    try:
        status = st.info("⏳ جاري صيد الصور من مصادر متعددة وتطبيق الزووم...")
        
        # معالجة الصوت
        audio_p = os.path.join(ASSETS_DIR, "v95_voice.mp3")
        if u_voice:
            with open(audio_p, "wb") as f: f.write(u_voice.getbuffer())
        else:
            gTTS(ai_text, lang='ar').save(audio_p)
        voice = AudioFileClip(audio_p)

        # تجهيز المشاهد
        sentences = [s.strip() for s in re.split(r'[.؟!،]+', ai_text) if len(s.strip()) > 1]
        dur_scene = voice.duration / len(sentences)
        h = 1080; w = int(h*9/16) if "9:16" in dim else int(h*16/9)
        
        img_clips = []
        
        

        for i, sent in enumerate(sentences):
            p = os.path.join(ASSETS_DIR, f"v95_img_{i}.jpg")
            get_pro_image(sent, p, (w, h), i)
            
            if os.path.exists(p):
                c = ImageClip(p).with_duration(dur_scene + 0.5)
                # زووم سينمائي Ken Burns
                z = 1.2 if i % 2 == 0 else 0.8
                c = c.resized(lambda t: 1 + (z-1) * (t / dur_scene))
                img_clips.append(c)

        # دمج النقلات الناعمة (Crossfade)
        video_track = concatenate_videoclips(img_clips, method="compose", padding=-0.4)

        # اللوجو
        if logo_file:
            logo_p = os.path.join(ASSETS_DIR, "logo_v95.png")
            Image.open(logo_file).convert("RGBA").resize((w//6, w//6)).save(logo_p)
            logo_clip = ImageClip(logo_p).with_duration(voice.duration).with_position(("right", "top"))
            final = CompositeVideoClip([video_track, logo_clip], size=(w, h)).with_audio(voice)
        else:
            final = CompositeVideoClip([video_track], size=(w, h)).with_audio(voice)

        out_f = os.path.join(VIDEOS_DIR, "Final_V95_Ultimate.mp4")
        final.write_videofile(out_f, fps=24, codec="libx264")
        st.video(out_f)

    except Exception as e:
        st.error(f"⚠️ خطأ: {str(e)}")
