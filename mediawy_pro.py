import streamlit as st
import os, requests, re, io, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import moviepy as mp
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip, vfx

# 1- إعداد البيئة (11- فواصل المجلدات)
MEDIA_DIR = "Mediawy_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- 4. محرك الصور المحصن ضد أخطاء الاختفاء ---
def get_guaranteed_image(sentence, path, size, index):
    w, h = size
    words = re.findall(r'\w+', sentence)
    search_term = words[0] if words else "vision"
    url = f"https://source.unsplash.com/featured/{w}x{h}/?{search_term},cinema&sig={random.randint(1,999)}"
    try:
        resp = requests.get(url, timeout=12)
        if resp.status_code == 200:
            img = Image.open(io.BytesIO(resp.content)).convert("RGB").resize(size)
            img.save(path, "JPEG")
    except: pass
    if not os.path.exists(path):
        img = Image.new("RGB", size, (20, 20, 35))
        draw = ImageDraw.Draw(img)
        draw.rectangle([20, 20, w-20, h-20], outline=(50, 100, 250), width=3)
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
    draw.text((x_pos, y_pos), text, font=font, fill="yellow")
    return ImageClip(np.array(img)).with_start(start_t).with_duration(dur)

# --- واجهة المستخدم (تطبيق الـ 11 إضافة) ---
st.set_page_config(page_title="Mediawy V94", layout="wide")
st.markdown("<h1 style='text-align:center; color:#00E5FF;'>🎬 Mediawy Studio V94 <span style='color:white;'>Stable Engine</span></h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ مركز التحكم")
    dim = st.selectbox("📏 2- الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    st.divider()
    audio_src = st.radio("🎙️ 3- مصدر الصوت:", ["بشري 🎤", "AI 🤖"])
    u_voice = st.file_uploader("ارفع صوتك هنا (بشري)") if "بشري" in audio_src else None
    ai_text = st.text_area("✍️ النص السينمائي:", value="الإرادة القوية هي التي تحول المستحيل إلى واقع ملموس.")
    st.divider()
    u_music = st.file_uploader("🎵 6- موسيقى خلفية")
    img_mode = st.radio("🖼️ 4- الصور:", ["أوتوماتيك", "رفع يدوي"])
    u_imgs = st.file_uploader("ارفع صورك يدوياً", accept_multiple_files=True)
    logo_file = st.file_uploader("9- اللوجو")

# --- محرك الرندر النهائي ---
if st.button("🚀 إطلاق رندر الإنجاز (V94)"):
    try:
        status = st.info("⏳ جاري دمج الصور وتطبيق النقلات الناعمة...")
        
        # [معالجة الصوت]
        audio_p = os.path.join(ASSETS_DIR, "v94_voice.mp3")
        if u_voice:
            with open(audio_p, "wb") as f: f.write(u_voice.getbuffer())
        else:
            gTTS(ai_text, lang='ar').save(audio_p)
        voice = AudioFileClip(audio_p)
        total_dur = voice.duration

        # [تجهيز المشاهد]
        sentences = [s.strip() for s in re.split(r'[.؟!،]+', ai_text) if len(s.strip()) > 1]
        dur_scene = total_dur / len(sentences)
        h = 1080; w = int(h*9/16) if "9:16" in dim else int(h*16/9)
        
        img_clips = []
        sub_clips = []

        for i, sent in enumerate(sentences):
            p = os.path.join(ASSETS_DIR, f"v94_img_{i}.jpg")
            if img_mode == "أوتوماتيك": get_guaranteed_image(sent, p, (w, h), i)
            elif u_imgs:
                with open(p, "wb") as f: f.write(u_imgs[i % len(u_imgs)].getbuffer())
            
            if os.path.exists(p):
                # زيادة مدة الكليب قليلاً لضمان التداخل الناعم (Padding)
                c = ImageClip(p).with_duration(dur_scene + 0.6)
                # 1, 5- تأثير الزووم السينمائي
                z = 1.15 if i % 2 == 0 else 0.85
                c = c.resized(lambda t: 1 + (z-1) * (t / dur_scene))
                img_clips.append(c)
                sub_clips.append(create_subtitle((w, h), sent, i*dur_scene, dur_scene))

        # 
        # استخدام طريقة compose مع padding سلبي لعمل نقلة ناعمة (Crossfade) أوتوماتيك
        video_track = concatenate_videoclips(img_clips, method="compose", padding=-0.5)

        # الهوية 9
        overlay = []
        if logo_file:
            logo_p = os.path.join(ASSETS_DIR, "v94_logo.png")
            Image.open(logo_file).convert("RGBA").resize((w//6, w//6)).save(logo_p)
            overlay.append(ImageClip(logo_p).with_duration(total_dur).with_position(("right", "top")))

        final = CompositeVideoClip([video_track] + overlay + sub_clips, size=(w, h)).with_audio(voice)
        out_f = os.path.join(VIDEOS_DIR, "Mediawy_V94_Stable.mp4")
        final.write_videofile(out_f, fps=24, codec="libx264")
        st.video(out_f)

    except Exception as e:
        st.error(f"⚠️ خطأ فني: {str(e)}")
