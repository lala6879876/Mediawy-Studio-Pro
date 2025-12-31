import streamlit as st
import os, requests, re, io, time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip, vfx

# 1- إعداد البيئة (11- فواصل المجلدات)
MEDIA_DIR = "Mediawy_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- 4. محرك الصور المحصن (منع خطأ No such file) ---
def get_safe_image(sentence, path, size, index):
    w, h = size
    words = re.findall(r'\w+', sentence)
    search_term = words[0] if words else "vision"
    
    # محاولة التحميل مع سياسة الـ "Re-try"
    url = f"https://source.unsplash.com/featured/{w}x{h}/?{search_term},cinema&sig={random.randint(1,1000)}"
    
    success = False
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            img = Image.open(io.BytesIO(resp.content)).convert("RGB").resize(size)
            img.save(path, "JPEG")
            # التأكد من الحفظ الفعلي قبل الخروج
            if os.path.exists(path): success = True
    except:
        success = False

    # لو الفشل حصل.. اصنع الصورة فوراً برمجياً لضمان وجود الملف
    if not success:
        img = Image.new("RGB", size, (20, 20, 30))
        draw = ImageDraw.Draw(img)
        # إضافة شكل جمالي بسيط عشان متبقاش سادة
        draw.rectangle([10, 10, w-10, h-10], outline=(index*50%255, 100, 200), width=5)
        img.save(path, "JPEG")
    
    return True

# --- 7. نصوص Clipchamp المضمونة ---
def create_subtitle(size, text, start_t, dur):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    f_size = size[0] // 16
    try: font = ImageFont.truetype("arial.ttf", f_size)
    except: font = ImageFont.load_default()
    
    tw = len(text) * (f_size * 0.65)
    th = f_size * 1.3
    y_pos, x_pos = int(size[1] * 0.75), (size[0] // 2) - (int(tw) // 2)
    draw.rectangle([x_pos-20, y_pos-10, x_pos+tw+20, y_pos+th+10], fill=(0,0,0,190))
    draw.text((x_pos, y_pos), text, font=font, fill="yellow")
    return ImageClip(np.array(img)).with_start(start_t).with_duration(dur)

# --- واجهة المستخدم (الـ 11 إضافة) ---
st.set_page_config(page_title="Mediawy V91", layout="wide")
st.markdown("<h1 style='text-align:center; color:#00E5FF;'>🎬 Mediawy Studio V91 Shield</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ مركز التحكم")
    dim = st.selectbox("📏 الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    audio_src = st.radio("🎙️ الصوت:", ["بشري 🎤", "AI 🤖"])
    u_voice = st.file_uploader("ارفع تعليقك الصوتي") if "بشري" in audio_src else None
    ai_text = st.text_area("✍️ النص:", value="الاصرار يحول الصعاب إلى نجاحات عظيمة.")
    st.divider()
    u_music = st.file_uploader("🎵 موسيقى خلفية")
    img_mode = st.radio("🖼️ الصور:", ["أوتوماتيك", "رفع يدوي"])
    u_imgs = st.file_uploader("ارفع صورك", accept_multiple_files=True)
    logo_file = st.file_uploader("9- اللوجو")

# --- محرك الرندر المحصن ---
if st.button("🚀 إطلاق الرندر المضمون (V91)"):
    try:
        import random
        status = st.info("⏳ جاري تحصين الملفات وبدء المونتاج...")
        
        # [الصوت]
        audio_p = os.path.join(ASSETS_DIR, "voice_v91.mp3")
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

        # [تأمين تحميل الصور قبل البدء]
        for i, sent in enumerate(sentences):
            p = os.path.join(ASSETS_DIR, f"v91_{i}.jpg")
            if img_mode == "أوتوماتيك":
                get_safe_image(sent, p, (w, h), i)
            else:
                with open(p, "wb") as f: f.write(u_imgs[i % len(u_imgs)].getbuffer())
            
            # فحص أخير لو الملف موجود فعلاً (الدرع الماسي)
            if not os.path.exists(p):
                time.sleep(1) # انتظر ثانية
            
            # بناء الكليب
            c = ImageClip(p).with_duration(dur_scene).crossfadein(0.5)
            z_factor = 1.15 if i % 2 == 0 else 0.85
            c = c.resized(lambda t: 1 + (z_factor-1) * (t / dur_scene))
            img_clips.append(c)
            sub_clips.append(create_subtitle((w, h), sent, i*dur_scene, dur_scene))

        video_track = concatenate_videoclips(img_clips, method="compose")

        # الهوية
        overlay = []
        if logo_file:
            logo = Image.open(logo_file).convert("RGBA").resize((w//6, w//6))
            logo_p = os.path.join(ASSETS_DIR, "logo_v91.png")
            logo.save(logo_p)
            overlay.append(ImageClip(logo_p).with_duration(voice.duration).with_position(("right", "top")))

        final = CompositeVideoClip([video_track] + overlay + sub_clips, size=(w, h)).with_audio(voice)
        out_f = os.path.join(VIDEOS_DIR, "Final_V91_Shield.mp4")
        final.write_videofile(out_f, fps=24, codec="libx264")
        st.video(out_f)

    except Exception as e:
        st.error(f"⚠️ خطأ: {str(e)}")
