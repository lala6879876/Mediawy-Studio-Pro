import streamlit as st
import os, requests, re, io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip, vfx

# 1- إعداد البيئة (11- فواصل الأداة)
MEDIA_DIR = "Mediawy_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- 4. محرك الفلترة الذكية (لضمان صور احترافية غير عشوائية) ---
def get_pro_image(sentence, path, size, index):
    w, h = size
    # فلترة الجملة واستخراج الكلمات الهامة فقط (Keywords Extraction)
    stop_words = ["من", "في", "على", "إلى", "عن", "مع", "هو", "هي", "كان", "ان", "هذا", "هذه"]
    words = re.findall(r'\w+', sentence)
    clean_words = [w for w in words if w not in stop_words and len(w) > 2]
    
    # بناء استعلام بحث احترافي (Professional Search Query)
    search_query = clean_words[0] if clean_words else "abstract+cinematic"
    # إضافة لمسات جمالية للبحث لضمان جودة الصور
    final_query = f"{search_query},professional,4k,wallpaper"
    
    url = f"https://source.unsplash.com/featured/{w}x{h}/?{final_query}&sig={index}"
    
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            img = Image.open(io.BytesIO(resp.content)).convert("RGB").resize(size)
            img.save(path, "JPEG")
            return True
    except:
        # لو فشل، بيصنع خلفية داكنة فخمة (Dark Theme) بدل الألوان العشوائية
        img = Image.new("RGB", size, (15, 15, 15))
        img.save(path, "JPEG")
        return True

# --- 7. نصوص Clipchamp بستايل "مودرن" ---
def create_modern_subtitle(size, text, start_t, dur):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    f_size = size[0] // 18
    try: font = ImageFont.truetype("arial.ttf", f_size)
    except: font = ImageFont.load_default()
    
    # حساب الأبعاد للنص العربي
    tw = len(text) * (f_size * 0.6)
    th = f_size * 1.2
    y_pos = int(size[1] * 0.8)
    x_pos = (size[0] // 2) - (int(tw) // 2)
    
    # خلفية شبه شفافة (Glassmorphism Style)
    draw.rectangle([x_pos-30, y_pos-15, x_pos+tw+30, y_pos+th+15], fill=(0,0,0,160), outline="yellow", width=2)
    draw.text((x_pos, y_pos), text, font=font, fill="white")
    return ImageClip(np.array(img)).with_start(start_t).with_duration(dur)

# --- واجهة المستخدم (تثبيت الـ 11 إضافة حرفياً) ---
st.set_page_config(page_title="Mediawy V89 Pro", layout="wide")
st.markdown("<h1 style='text-align:center; color:#FFD700;'>🎬 Mediawy Studio V89 <span style='color:white;'>Elite</span></h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ رادار الجودة")
    dim = st.selectbox("📏 الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    st.divider()
    audio_src = st.radio("🎙️ مصدر الصوت:", ["بشري 🎤", "AI 🤖"])
    u_voice = st.file_uploader("ارفع تعليقك الصوتي") if "بشري" in audio_src else None
    ai_text = st.text_area("✍️ النص السينمائي (جمل قصيرة):", value="الإرادة القوية تكسر المستحيل. ابدأ الآن.")
    st.divider()
    bg_music = st.file_uploader("🎵 موسيقى خلفية هادئة")
    st.divider()
    logo_file = st.file_uploader("🖼️ اللوجو (الهوية)")

# --- محرك الرندر الملياري ---
if st.button("🚀 إطلاق رندر النخبة (بدون أخطاء)"):
    try:
        status = st.info("⏳ جاري تحليل المحتوى وفلترة الصور السينمائية...")
        
        # معالجة الصوت
        audio_p = os.path.join(ASSETS_DIR, "v.mp3")
        if u_voice:
            with open(audio_p, "wb") as f: f.write(u_voice.getbuffer())
        else:
            gTTS(ai_text, lang='ar').save(audio_p)
        voice = AudioFileClip(audio_p)
        
        # معالجة الموسيقى
        final_audio = voice
        if bg_music:
            m_p = os.path.join(ASSETS_DIR, "m.mp3")
            with open(m_p, "wb") as f: f.write(bg_music.getbuffer())
            bg = AudioFileClip(m_p).subclipped(0, voice.duration).with_effects([vfx.AudioVolumize(0.1)])
            final_audio = CompositeAudioClip([voice, bg])

        # بناء المشاهد
        sentences = [s.strip() for s in re.split(r'[.؟!،]+', ai_text) if len(s.strip()) > 1]
        dur_scene = voice.duration / len(sentences)
        h = 1080; w = int(h*9/16) if "9:16" in dim else int(h*16/9)
        
        img_clips = []
        sub_clips = []

        for i, sent in enumerate(sentences):
            p = os.path.join(ASSETS_DIR, f"elite_{i}.jpg")
            get_pro_image(sent, p, (w, h), i)
            
            # زووم ناعم وتأثيرات بصرية (FX)
            c = ImageClip(p).with_duration(dur_scene).crossfadein(0.5)
            z_mode = 1.15 if i % 2 == 0 else 0.85
            c = c.resized(lambda t: 1 + (z_mode-1) * (t / dur_scene))
            img_clips.append(c)
            sub_clips.append(create_modern_subtitle((w, h), sent, i*dur_scene, dur_scene))

        video_track = concatenate_videoclips(img_clips, method="compose")

        # الهوية 9
        overlay = []
        if logo_file:
            logo = Image.open(logo_file).convert("RGBA").resize((w//6, w//6))
            logo_p = os.path.join(ASSETS_DIR, "logo.png")
            logo.save(logo_p)
            overlay.append(ImageClip(logo_p).with_duration(voice.duration).with_position(("right", "top")))

        final = CompositeVideoClip([video_track] + overlay + sub_clips, size=(w, h)).with_audio(final_audio)
        out_f = os.path.join(VIDEOS_DIR, "Elite_Mediawy_V89.mp4")
        final.write_videofile(out_f, fps=24, codec="libx264")
        st.video(out_f)

    except Exception as e:
        st.error(f"⚠️ خطأ فني: {str(e)}")
