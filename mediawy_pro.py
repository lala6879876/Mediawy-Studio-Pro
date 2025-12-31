import streamlit as st
import os, requests, re, io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import moviepy as mp
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip, vfx

# 1- إعداد البيئة والمجلدات (11- فواصل الأداة)
if os.name == 'posix': os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"
MEDIA_DIR = "Mediawy_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- 4. محرك الصور السياقي المطور (أوتو/رفع) ---
def get_verified_image(query, path, size, index):
    w, h = size
    # تنظيف الكلمة للبحث (أول كلمتين من الجملة) لضمان السياق
    clean_q = "+".join(re.findall(r'\w+', query)[:2])
    url = f"https://loremflickr.com/{w}/{h}/{clean_q if clean_q else 'cinematic'}"
    try:
        resp = requests.get(url, timeout=12)
        img = Image.open(io.BytesIO(resp.content)).convert("RGB").resize(size)
        img.save(path, "JPEG")
        return True
    except:
        # خلفية تدرج لوني سينمائي لو النت تعثر
        base = Image.new("RGB", size, (20, 20, 20))
        draw = ImageDraw.Draw(base)
        draw.rectangle([0, 0, w, h], fill=(index*35%255, 45, 95))
        base.save(path, "JPEG")
        return True

# --- 7. محرك نصوص Clipchamp (الترجمة الذكية) ---
def create_subtitle(size, text, start_t, dur):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    f_size = size[0] // 16
    try: font = ImageFont.truetype("arial.ttf", f_size)
    except: font = ImageFont.load_default()
    # تنسيق النص
    tw = len(text) * (f_size * 0.65)
    th = f_size * 1.3
    y_pos, x_pos = int(size[1] * 0.75), (size[0] // 2) - (int(tw) // 2)
    # رسم الصندوق الاحترافي
    draw.rectangle([x_pos-20, y_pos-10, x_pos+tw+20, y_pos+th+10], fill=(0,0,0,200))
    draw.text((x_pos, y_pos), text, font=font, fill="#FFD700") # أصفر ذهبي
    return ImageClip(np.array(img)).with_start(start_t).with_duration(dur)

# --- واجهة المستخدم (الـ 11 إضافة كاملة) ---
st.set_page_config(page_title="Mediawy V84", layout="wide")
st.markdown("<h1 style='text-align:center; color:#00E5FF;'>🎬 Mediawy Studio V84 Master</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ مركز التحكم")
    dim = st.selectbox("📏 2- الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    edit_style = st.selectbox("🎭 1- النمط:", ["سينمائي 🎬", "درامي 🎭", "وثائقي 📜"])
    st.divider()

    # 3- ركن الصوت (بشري/AI)
    st.subheader("🎙️ 3- الصوت (رفع بشري)")
    audio_src = st.radio("المصدر:", ["بشري (ارفع ملفك) 🎤", "AI (الذكاء الاصطناعي) 🤖"])
    u_voice = st.file_uploader("📁 ارفع تعليقك الصوتي") if "بشري" in audio_src else None
    ai_text = st.text_area("✍️ النص (للمزامنة والترجمة):", value="مرحباً بكم في ميدياوي استوديو، حيث تتحول الأفكار إلى واقع سينمائي.")
    st.divider()

    # 6- ركن الموسيقى
    st.subheader("🎵 6- الموسيقى الخلفية")
    bg_music_opt = st.toggle("تفعيل الموسيقى", value=True)
    u_music = st.file_uploader("📁 ارفع موسيقى MP3 من جهازك")
    st.divider()

    # 4- ركن الصور
    st.subheader("🖼️ 4- الصور")
    img_mode = st.radio("الجلب:", ["أوتوماتيك (حسب السياق)", "رفع يدوي"])
    u_imgs = st.file_uploader("📁 ارفع صورك (حتى 500)", accept_multiple_files=True)
    st.divider()

    # 8, 9- الهوية
    show_banner = st.toggle("8- بنر سفلي", value=True)
    logo_file = st.file_uploader("9- اللوجو")

# --- محرك الرندر النهائي (التأثيرات والزووم 1، 5) ---
if st.button("🚀 إطلاق الرندر الملياري (V84)"):
    try:
        status = st.info("⏳ جاري دمج الأركان وتطبيق التأثيرات السينمائية...")
        
        # [معالجة الصوت]
        audio_p = os.path.join(ASSETS_DIR, "v.mp3")
        if u_voice:
            with open(audio_p, "wb") as f: f.write(u_voice.getbuffer())
        else:
            gTTS(ai_text, lang='ar').save(audio_p)
        voice = AudioFileClip(audio_p)
        total_dur = voice.duration

        # [معالجة الموسيقى 6]
        final_audio = voice
        if bg_music_opt and u_music:
            m_p = os.path.join(ASSETS_DIR, "m.mp3")
            with open(m_p, "wb") as f: f.write(u_music.getbuffer())
            bg = AudioFileClip(m_p).subclipped(0, total_dur).with_effects([vfx.AudioVolumize(0.12)])
            final_audio = CompositeAudioClip([voice, bg])

        # [بناء المشاهد 1، 4، 5، 7]
        sentences = [s.strip() for s in re.split(r'[.؟!،]+', ai_text) if len(s.strip()) > 1]
        dur_scene = total_dur / len(sentences)
        h = 1080; w = int(h*9/16) if "9:16" in dim else int(h*16/9)
        
        img_clips = []
        sub_clips = []

        for i, sent in enumerate(sentences):
            p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
            if img_mode == "أوتوماتيك (حسب السياق)":
                get_verified_image(sent, p, (w, h), i)
            else:
                with open(p, "wb") as f: f.write(u_imgs[i % len(u_imgs)].getbuffer())
            
            # زووم ناعم Ken Burns ونقلات 1، 5
            c = ImageClip(p).with_duration(dur_scene).crossfadein(0.5)
            z_val = 1.18 if i % 2 == 0 else 0.82
            c = c.resized(lambda t: 1 + (z_val-1) * (t / dur_scene))
            img_clips.append(c)
            # 7- نصوص الترجمة
            sub_clips.append(create_subtitle((w, h), sent, i*dur_scene, dur_scene))

        video_track = concatenate_videoclips(img_clips, method="compose")

        # [8, 9- الهوية]
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        if logo_file:
            logo = Image.open(logo_file).convert("RGBA").resize((w//6, w//6))
            overlay.paste(logo, (w-w//6-30, 30), logo)
        if show_banner:
            draw = ImageDraw.Draw(overlay)
            draw.rectangle([0, h-100, w, h], fill=(0,0,0,220))
            draw.text((40, h-75), "Mediawy Studio - Powered by AI", fill="white")
        static_layer = ImageClip(np.array(overlay)).with_duration(total_dur)

        # الرندر الشامل
        final = CompositeVideoClip([video_track, static_layer] + sub_clips, size=(w, h)).with_audio(final_audio)
        out_f = os.path.join(VIDEOS_DIR, "Mediawy_Success_V84.mp4")
        final.write_videofile(out_f, fps=24, codec="libx264")
        st.video(out_f)
        
        # 10- SEO
        st.divider()
        st.subheader("📋 10- SEO ونشر")
        st.code(f"العنوان: {sentences[0][:40]} \n#Mediawy #Shorts #Success")

    except Exception as e:
        st.error(f"⚠️ خطأ فني: {str(e)}")
