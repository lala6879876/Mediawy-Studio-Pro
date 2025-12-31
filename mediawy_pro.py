import streamlit as st
import os, requests, re, io, time, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip, vfx

# 1- إعداد البيئة (11- فواصل المجلدات)
MEDIA_DIR = "Mediawy_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- 4. محرك الصور الانتحاري (ضمان التغير والارتباط) ---
def get_verified_image(sentence, path, size, index):
    w, h = size
    # استخراج الكلمات المفتاحية
    words = re.findall(r'\w+', sentence)
    search_term = words[0] if words else "abstract"
    
    # استخدام رابط ديناميكي مع "بصمة زمنية" لمنع التكرار (Cache Busting)
    timestamp = int(time.time()) + index
    url = f"https://source.unsplash.com/featured/{w}x{h}/?{search_term},cinema&sig={timestamp}"
    
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            img = Image.open(io.BytesIO(resp.content)).convert("RGB").resize(size)
            img.save(path, "JPEG")
            return True
    except:
        # لو السيرفر وقع، نصنع خلفية سينمائية "تدرج لوني" ونكتب عليها النص
        img = Image.new("RGB", size, (10, 10, 10))
        draw = ImageDraw.Draw(img)
        # تدرج لوني بسيط
        draw.rectangle([0, 0, w, h], fill=(random.randint(20,60), 20, random.randint(50,100)))
        img.save(path, "JPEG")
        return True

# --- 7. نصوص Clipchamp الاحترافية ---
def create_subtitle(size, text, start_t, dur):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    f_size = size[0] // 16
    try: font = ImageFont.truetype("arial.ttf", f_size)
    except: font = ImageFont.load_default()
    
    tw = len(text) * (f_size * 0.6)
    th = f_size * 1.2
    y_pos, x_pos = int(size[1] * 0.75), (size[0] // 2) - (int(tw) // 2)
    
    draw.rectangle([x_pos-20, y_pos-10, x_pos+tw+20, y_pos+th+10], fill=(0,0,0,180))
    draw.text((x_pos, y_pos), text, font=font, fill="#FFD700")
    return ImageClip(np.array(img)).with_start(start_t).with_duration(dur)

# --- واجهة المستخدم (تطبيق الـ 11 إضافة) ---
st.set_page_config(page_title="Mediawy V90", layout="wide")
st.markdown("<h1 style='text-align:center; color:#00E5FF;'>🎬 Mediawy Studio V90 Master</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ لوحة التحكم")
    dim = st.selectbox("📏 2- الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    st.divider()
    
    # 3- ركن الصوت
    st.subheader("🎙️ 3- الصوت (بشري/AI)")
    audio_src = st.radio("المصدر:", ["بشري 🎤", "AI 🤖"])
    u_voice = st.file_uploader("ارفع تعليقك الصوتي") if "بشري" in audio_src else None
    ai_text = st.text_area("✍️ النص:", value="العمل الجاد هو مفتاح النجاح. ابدأ رحلتك اليوم.")
    st.divider()

    # 6- ركن الموسيقى
    st.subheader("🎵 6- موسيقى خلفية")
    u_music = st.file_uploader("ارفع ملف موسيقى هادئة")
    st.divider()

    # 4- ركن الصور
    img_mode = st.radio("🖼️ 4- الصور:", ["أوتوماتيك", "رفع يدوي"])
    u_imgs = st.file_uploader("ارفع صورك يدوياً", accept_multiple_files=True)
    logo_file = st.file_uploader("9- اللوجو")

# --- محرك الرندر ---
if st.button("🚀 إطلاق الرندر المصلح (V90)"):
    try:
        status = st.info("⏳ جاري سحب صور جديدة وتطبيق الزووم السينمائي...")
        
        # [الصوت]
        audio_p = os.path.join(ASSETS_DIR, "v.mp3")
        if u_voice:
            with open(audio_p, "wb") as f: f.write(u_voice.getbuffer())
        else:
            gTTS(ai_text, lang='ar').save(audio_p)
        voice = AudioFileClip(audio_p)

        # [الموسيقى 6]
        final_audio = voice
        if u_music:
            m_p = os.path.join(ASSETS_DIR, "m.mp3")
            with open(m_p, "wb") as f: f.write(u_music.getbuffer())
            bg = AudioFileClip(m_p).subclipped(0, voice.duration).with_effects([vfx.AudioVolumize(0.1)])
            final_audio = CompositeAudioClip([voice, bg])

        # [بناء المشاهد]
        sentences = [s.strip() for s in re.split(r'[.؟!،]+', ai_text) if len(s.strip()) > 1]
        dur_scene = voice.duration / len(sentences)
        h = 1080; w = int(h*9/16) if "9:16" in dim else int(h*16/9)
        
        img_clips = []
        sub_clips = []

        for i, sent in enumerate(sentences):
            p = os.path.join(ASSETS_DIR, f"v90_{i}.jpg")
            if img_mode == "أوتوماتيك":
                get_verified_image(sent, p, (w, h), i)
            else:
                with open(p, "wb") as f: f.write(u_imgs[i % len(u_imgs)].getbuffer())
            
            # زووم ناعم وتأثيرات 1، 5
            c = ImageClip(p).with_duration(dur_scene).crossfadein(0.5)
            z_factor = 1.2 if i % 2 == 0 else 0.8
            c = c.resized(lambda t: 1 + (z_factor-1) * (t / dur_scene))
            img_clips.append(c)
            sub_clips.append(create_subtitle((w, h), sent, i*dur_scene, dur_scene))

        video_track = concatenate_videoclips(img_clips, method="compose")

        # الهوية 9
        overlay = []
        if logo_file:
            logo = Image.open(logo_file).convert("RGBA").resize((w//6, w//6))
            logo_p = os.path.join(ASSETS_DIR, "logo.png")
            logo.save(logo_p)
            overlay.append(ImageClip(logo_p).with_duration(voice.duration).with_position(("right", "top")))

        final = CompositeVideoClip([video_track] + overlay + sub_clips, size=(w, h)).with_audio(final_audio)
        out_f = os.path.join(VIDEOS_DIR, "Final_V90.mp4")
        final.write_videofile(out_f, fps=24, codec="libx264")
        st.video(out_f)

    except Exception as e:
        st.error(f"⚠️ خطأ: {str(e)}")
