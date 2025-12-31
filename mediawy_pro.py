import streamlit as st
import os, requests, re, io, time, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip, vfx

# 1- إعداد البيئة (تأمين المجلدات)
MEDIA_DIR = "Mediawy_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- 4. محرك "صياد الصور" المحدث (استخدام محركات بحث مفتوحة ومستقرة) ---
def get_guaranteed_image(sentence, path, size, index):
    w, h = size
    # تنقية الجملة للبحث الاحترافي
    stop_words = ["من", "في", "على", "إلى", "هو", "هي"]
    words = [w for w in re.findall(r'\w+', sentence) if w not in stop_words and len(w) > 2]
    q = words[0] if words else "cinematic"
    
    # مصادر صور عالية الجودة جداً (HD) ومستقرة
    sources = [
        f"https://loremflickr.com/g/{w}/{h}/{q}?lock={random.randint(1,1000)}",
        f"https://picsum.photos/seed/{random.randint(1,1000)}/{w}/{h}",
        f"https://api.duckduckgo.com/ia/?q={q}&format=json" # محاكاة بحث صور
    ]
    
    for url in sources:
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                img = Image.open(io.BytesIO(resp.content)).convert("RGB").resize(size)
                img.save(path, "JPEG")
                if os.path.exists(path) and os.path.getsize(path) > 1000: # التأكد إنها صورة حقيقية مش فارغة
                    return True
        except:
            continue

    # لو كل المصادر فشلت، نصنع خلفية "سينمائية" فخمة (Dark Gradient)
    base = Image.new("RGB", size, (10, 10, 15))
    draw = ImageDraw.Draw(base)
    draw.rectangle([0, 0, w, h], fill=(index*30%50, 20, 40))
    base.save(path, "JPEG")
    return True

# --- واجهة المستخدم (تثبيت الـ 11 إضافة بالكامل) ---
st.set_page_config(page_title="Mediawy V96 Master", layout="wide")
st.markdown("<h1 style='text-align:center; color:#FFD700;'>🎬 Mediawy Studio V96 <span style='color:white;'>Master Pro</span></h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ لوحة المونتاج")
    dim = st.selectbox("📏 الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    st.divider()
    audio_src = st.radio("🎙️ الصوت:", ["بشري 🎤", "AI 🤖"])
    u_voice = st.file_uploader("ارفع تعليقك الصوتي") if "بشري" in audio_src else None
    ai_text = st.text_area("✍️ النص السينمائي:", value="الإبداع لا يحده حدود، والنجاح هو ثمرة الإصرار.")
    st.divider()
    u_music = st.file_uploader("🎵 موسيقى خلفية")
    logo_file = st.file_uploader("🖼️ اللوجو")

# --- محرك الرندر ---
if st.button("🚀 إطلاق رندر الإنجاز (V96)"):
    try:
        status = st.info("⏳ جاري سحب الصور من مصادر HD... وتطبيق تأثيرات الحركة...")
        
        # [معالجة الصوت]
        audio_p = os.path.join(ASSETS_DIR, "voice_v96.mp3")
        if u_voice:
            with open(audio_p, "wb") as f: f.write(u_voice.getbuffer())
        else:
            gTTS(ai_text, lang='ar').save(audio_p)
        voice = AudioFileClip(audio_p)

        # [تجهيز المشاهد]
        sentences = [s.strip() for s in re.split(r'[.؟!،]+', ai_text) if len(s.strip()) > 1]
        dur_scene = voice.duration / len(sentences)
        h = 1080; w = int(h*9/16) if "9:16" in dim else int(h*16/9)
        
        img_clips = []
        
        

        for i, sent in enumerate(sentences):
            p = os.path.join(ASSETS_DIR, f"v96_img_{i}.jpg")
            get_guaranteed_image(sent, p, (w, h), i)
            
            if os.path.exists(p):
                # تأثير الزووم (Ken Burns) المطور 1, 5
                c = ImageClip(p).with_duration(dur_scene + 0.6)
                z = 1.2 if i % 2 == 0 else 0.8
                c = c.resized(lambda t: 1 + (z-1) * (t / dur_scene))
                img_clips.append(c)

        # دمج النقلات الناعمة (Crossfade) أوتوماتيكياً
        video_track = concatenate_videoclips(img_clips, method="compose", padding=-0.5)

        # دمج الموسيقى الخلفية
        final_audio = voice
        if u_music:
            m_p = os.path.join(ASSETS_DIR, "bg_v96.mp3")
            with open(m_p, "wb") as f: f.write(u_music.getbuffer())
            bg = AudioFileClip(m_p).subclipped(0, voice.duration).with_effects([vfx.AudioVolumize(0.12)])
            final_audio = CompositeAudioClip([voice, bg])

        # اللوجو
        overlay = []
        if logo_file:
            logo_p = os.path.join(ASSETS_DIR, "logo_v96.png")
            Image.open(logo_file).convert("RGBA").resize((w//6, w//6)).save(logo_p)
            overlay.append(ImageClip(logo_p).with_duration(voice.duration).with_position(("right", "top")))

        final = CompositeVideoClip([video_track] + overlay, size=(w, h)).with_audio(final_audio)
        out_f = os.path.join(VIDEOS_DIR, "Final_Mediawy_V96.mp4")
        final.write_videofile(out_f, fps=24, codec="libx264")
        st.video(out_f)

    except Exception as e:
        st.error(f"⚠️ خطأ: {str(e)}")
