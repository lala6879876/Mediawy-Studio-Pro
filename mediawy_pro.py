import streamlit as st
import os, requests, re, io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import moviepy as mp
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip, vfx

# 1- إعداد المجلدات (11- فواصل الأداة)
MEDIA_DIR = "Mediawy_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- محرك الصور الذكي (تجنب الفشل والخلفية الزرقاء) ---
def get_verified_image(query, path, size, index):
    w, h = size
    # محاولة جلب صورة حقيقية مرتبطة بالموضوع
    clean_q = "+".join(re.findall(r'\w+', query)[:2])
    # استخدام رابط أكثر استقراراً
    url = f"https://loremflickr.com/{w}/{h}/{clean_q if clean_q else 'tech'}"
    try:
        resp = requests.get(url, timeout=10)
        img = Image.open(io.BytesIO(resp.content)).convert("RGB").resize(size)
        img.save(path, "JPEG")
        return True
    except:
        # لو النت فشل، بنعمل "تدرج لوني سينمائي" (Gradient) بدل اللون الأزرق السادة
        base = Image.new("RGB", size, (20, 20, 20))
        draw = ImageDraw.Draw(base)
        draw.rectangle([0, 0, w, h], fill=(index*30%255, 40, 100))
        base.save(path, "JPEG")
        return True

# --- واجهة المستخدم (تثبيت الـ 11 إضافة) ---
st.set_page_config(page_title="Mediawy V82", layout="wide")
st.markdown("<h1 style='text-align:center; color:#00E5FF;'>🎬 Mediawy Studio V82 Master</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ لوحة التحكم")
    dim = st.selectbox("📏 2- الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    st.divider()

    st.subheader("🎙️ 3- الصوت (بشري/AI)")
    audio_src = st.radio("المصدر:", ["بشري 🎤", "AI (GTTS) 🤖"])
    u_voice = st.file_uploader("📁 ارفع صوتك (3)") if "بشري" in audio_src else None
    ai_text = st.text_area("✍️ النص (للترجمة):", value="الإبداع هو روح العمل، ميدياوي استوديو يحول أفكارك لواقع.")
    st.divider()

    st.subheader("🎵 6- الموسيقى")
    bg_music_opt = st.toggle("تفعيل الموسيقى", value=True)
    u_music = st.file_uploader("📁 ارفع موسيقى (6)")
    st.divider()

    st.subheader("🖼️ 4- الصور")
    img_mode = st.radio("النمط:", ["أوتوماتيك (سياقي)", "رفع يدوي"])
    u_imgs = st.file_uploader("📁 ارفع صورك (4)", accept_multiple_files=True)
    st.divider()

    logo_file = st.file_uploader("9- اللوجو (9)")

# --- محرك الرندر النهائي ---
if st.button("🚀 إطلاق الرندر الملياري"):
    try:
        status = st.info("⏳ جاري المونتاج... جلب الصور السياقية... تطبيق الزووم...")
        
        # [الصوت]
        audio_p = os.path.join(ASSETS_DIR, "v.mp3")
        if u_voice:
            with open(audio_p, "wb") as f: f.write(u_voice.getbuffer())
        else:
            gTTS(ai_text, lang='ar').save(audio_p)
        voice = AudioFileClip(audio_p)
        total_dur = voice.duration

        # [الموسيقى]
        final_audio = voice
        if bg_music_opt and u_music:
            m_p = os.path.join(ASSETS_DIR, "m.mp3")
            with open(m_p, "wb") as f: f.write(u_music.getbuffer())
            bg = AudioFileClip(m_p).subclipped(0, total_dur).with_effects([vfx.AudioVolumize(0.15)])
            final_audio = CompositeAudioClip([voice, bg])

        # [بناء المشاهد والزووم 1، 5]
        sentences = [s.strip() for s in re.split(r'[.؟!،]+', ai_text) if len(s.strip()) > 1]
        dur_scene = total_dur / len(sentences)
        h = 1080; w = int(h*9/16) if "9:16" in dim else int(h*16/9)
        
        img_clips = []
        for i, sent in enumerate(sentences):
            p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
            if img_mode == "أوتوماتيك":
                get_verified_image(sent, p, (w, h), i)
            else:
                with open(p, "wb") as f: f.write(u_imgs[i % len(u_imgs)].getbuffer())
            
            # زووم حقيقي (Ken Burns) ونقلات ناعمة
            c = ImageClip(p).with_duration(dur_scene + 0.5)
            z = 1.2 if i % 2 == 0 else 0.8
            c = c.resized(lambda t: 1 + (z-1) * (t / dur_scene))
            img_clips.append(c)

        # دمج المشاهد بنقلات Compose
        video_track = concatenate_videoclips(img_clips, method="compose", padding=-0.5)

        # [الهوية 9]
        if logo_file:
            logo = Image.open(logo_file).convert("RGBA").resize((w//6, w//6))
            logo_path = os.path.join(ASSETS_DIR, "logo.png")
            logo.save(logo_path)
            logo_clip = ImageClip(logo_path).with_duration(total_dur).with_position(("right", "top")).with_start(0)
            final_vid = CompositeVideoClip([video_track, logo_clip], size=(w, h))
        else:
            final_vid = CompositeVideoClip([video_track], size=(w, h))

        # الرندر
        out_f = os.path.join(VIDEOS_DIR, "Mediawy_V82_Final.mp4")
        final_vid.with_audio(final_audio).write_videofile(out_f, fps=24, codec="libx264")
        st.video(out_f)
        
        # 10- SEO
        st.divider()
        st.code(f"Title: {sentences[0][:40]} #Mediawy #AI #Shorts")

    except Exception as e:
        st.error(f"⚠️ خطأ فني: {str(e)}")
