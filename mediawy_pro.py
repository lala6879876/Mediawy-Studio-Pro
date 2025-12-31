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

# --- 4. محرك الصور المضمون (التحقق الاستباقي) ---
def get_guaranteed_image(sentence, path, size, index):
    w, h = size
    words = re.findall(r'\w+', sentence)
    search_term = words[0] if words else "creative"
    
    # محاولة التحميل مع بصمة زمنية لمنع الكاش
    url = f"https://source.unsplash.com/featured/{w}x{h}/?{search_term}&sig={random.randint(1,1000)}"
    
    try:
        resp = requests.get(url, timeout=12)
        if resp.status_code == 200:
            img = Image.open(io.BytesIO(resp.content)).convert("RGB").resize(size)
            img.save(path, "JPEG")
    except:
        pass # سنقوم بمعالجة الفشل في الخطوة التالية

    # الدرع الماسي: لو الملف مش موجود بعد المحاولة، نصنعه فوراً
    if not os.path.exists(path):
        # توليد صورة سينمائية داكنة (Placeholder)
        img = Image.new("RGB", size, (20, 20, 35))
        draw = ImageDraw.Draw(img)
        # مظهر احترافي بدل الفراغ
        draw.rectangle([30, 30, w-30, h-30], outline=(70, 130, 250), width=4)
        img.save(path, "JPEG")
    
    return True

# --- 7. نصوص Clipchamp الاحترافية ---
def create_subtitle(size, text, start_t, dur):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    f_size = size[0] // 16
    try: font = ImageFont.truetype("arial.ttf", f_size)
    except: font = ImageFont.load_default()
    
    tw = len(text) * (f_size * 0.65)
    th = f_size * 1.3
    y_pos, x_pos = int(size[1] * 0.75), (size[0] // 2) - (int(tw) // 2)
    draw.rectangle([x_pos-20, y_pos-10, x_pos+tw+20, y_pos+th+10], fill=(0,0,0,200))
    draw.text((x_pos, y_pos), text, font=font, fill="#FFD700")
    return ImageClip(np.array(img)).with_start(start_t).with_duration(dur)

# --- واجهة المستخدم (الـ 11 إضافة كاملة) ---
st.set_page_config(page_title="Mediawy V93 Shield", layout="wide")
st.markdown("<h1 style='text-align:center; color:#00E5FF;'>🎬 Mediawy Studio V93 <span style='color:white;'>Elite Shield</span></h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ لوحة التحكم")
    dim = st.selectbox("📏 الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    st.divider()
    audio_src = st.radio("🎙️ مصدر الصوت:", ["بشري 🎤", "AI 🤖"])
    u_voice = st.file_uploader("ارفع تعليقك الصوتي") if "بشري" in audio_src else None
    ai_text = st.text_area("✍️ النص:", value="الاصرار هو ما يحول الفشل إلى انجاز عظيم.")
    st.divider()
    u_music = st.file_uploader("🎵 موسيقى خلفية")
    img_mode = st.radio("🖼️ الصور:", ["أوتوماتيك", "رفع يدوي"])
    u_imgs = st.file_uploader("ارفع صورك", accept_multiple_files=True)
    logo_file = st.file_uploader("9- اللوجو")

# --- محرك الرندر المضمون ---
if st.button("🚀 إطلاق رندر الحصن (V93)"):
    try:
        status = st.info("⏳ جاري تأمين الأصول الرقمية والتأكد من وجود الملفات...")
        
        # [معالجة الصوت]
        audio_p = os.path.join(ASSETS_DIR, "voice_v93.mp3")
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
        sub_clips = []

        # 
        
        # المرحلة الأولى: التأكد من تحميل كل الصور
        for i, sent in enumerate(sentences):
            p = os.path.join(ASSETS_DIR, f"v93_img_{i}.jpg")
            if img_mode == "أوتوماتيك":
                get_guaranteed_image(sent, p, (w, h), i)
            elif u_imgs:
                with open(p, "wb") as f: f.write(u_imgs[i % len(u_imgs)].getbuffer())
            
            # المرحلة الثانية: بناء الكليبات فقط للملفات التي تم التأكد من وجودها
            if os.path.exists(p):
                c = ImageClip(p).with_duration(dur_scene).crossfadein(0.5)
                # تأثير الزووم 1، 5
                z_factor = 1.18 if i % 2 == 0 else 0.82
                c = c.resized(lambda t: 1 + (z_factor-1) * (t / dur_scene))
                img_clips.append(c)
                sub_clips.append(create_subtitle((w, h), sent, i*dur_scene, dur_scene))

        # دمج المشاهد بنظام Compose الآمن
        video_track = concatenate_videoclips(img_clips, method="compose")

        # الهوية 9
        overlay = []
        if logo_file:
            logo_p = os.path.join(ASSETS_DIR, "logo_v93.png")
            Image.open(logo_file).convert("RGBA").resize((w//6, w//6)).save(logo_p)
            overlay.append(ImageClip(logo_p).with_duration(voice.duration).with_position(("right", "top")))

        final = CompositeVideoClip([video_track] + overlay + sub_clips, size=(w, h)).with_audio(voice)
        out_f = os.path.join(VIDEOS_DIR, "Mediawy_V93_Shield.mp4")
        final.write_videofile(out_f, fps=24, codec="libx264")
        st.video(out_f)

    except Exception as e:
        st.error(f"⚠️ خطأ فني: {str(e)}")
