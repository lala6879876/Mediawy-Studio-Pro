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

# --- 4. محرك الصور المحصن (منع خطأ No such file نهائياً) ---
def get_guaranteed_image(sentence, path, size, index):
    w, h = size
    words = re.findall(r'\w+', sentence)
    search_term = words[0] if words else "vision"
    
    # محاولة التحميل من مصدر مستقر
    url = f"https://source.unsplash.com/featured/{w}x{h}/?{search_term},cinema&sig={random.randint(1,999)}"
    
    success = False
    try:
        resp = requests.get(url, timeout=12)
        if resp.status_code == 200:
            img = Image.open(io.BytesIO(resp.content)).convert("RGB").resize(size)
            img.save(path, "JPEG")
            if os.path.exists(path): success = True
    except:
        success = False

    # الكارت الرابح: لو التحميل فشل أو اتأخر، نصنع ملف فوراً بنفس الاسم لضمان عدم توقف الرندر
    if not success:
        # صنع خلفية سينمائية داكنة احترافية
        img = Image.new("RGB", size, (15, 15, 25))
        draw = ImageDraw.Draw(img)
        # رسم مستطيل جمالي لإعطاء مظهر "تصميم" وليس مجرد سواد
        draw.rectangle([20, 20, w-20, h-20], outline=(50, 100, 250), width=3)
        img.save(path, "JPEG")
    
    return True

# --- 7. نصوص Clipchamp بستايل Master ---
def create_subtitle(size, text, start_t, dur):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    f_size = size[0] // 16
    try: font = ImageFont.truetype("arial.ttf", f_size)
    except: font = ImageFont.load_default()
    
    tw = len(text) * (f_size * 0.65)
    th = f_size * 1.3
    y_pos, x_pos = int(size[1] * 0.75), (size[0] // 2) - (int(tw) // 2)
    # صندوق نص احترافي
    draw.rectangle([x_pos-20, y_pos-10, x_pos+tw+20, y_pos+th+10], fill=(0,0,0,200))
    draw.text((x_pos, y_pos), text, font=font, fill="yellow")
    return ImageClip(np.array(img)).with_start(start_t).with_duration(dur)

# --- واجهة المستخدم (الـ 11 إضافة كاملة) ---
st.set_page_config(page_title="Mediawy V92", layout="wide")
st.markdown("<h1 style='text-align:center; color:#00E5FF;'>🎬 Mediawy Studio V92 <span style='color:white;'>Shield</span></h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ مركز التحكم")
    dim = st.selectbox("📏 2- الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    st.divider()
    audio_src = st.radio("🎙️ 3- مصدر الصوت:", ["بشري 🎤", "AI 🤖"])
    u_voice = st.file_uploader("ارفع صوتك هنا (بشري)") if "بشري" in audio_src else None
    ai_text = st.text_area("✍️ النص السينمائي:", value="القوة لا تأتي من النجاح، بل من الصمود في وجه التحديات.")
    st.divider()
    u_music = st.file_uploader("🎵 6- موسيقى خلفية (اختياري)")
    img_mode = st.radio("🖼️ 4- الصور:", ["أوتوماتيك", "رفع يدوي"])
    u_imgs = st.file_uploader("ارفع صورك يدوياً", accept_multiple_files=True)
    logo_file = st.file_uploader("9- اللوجو (الهوية)")

# --- محرك الرندر المضمون ---
if st.button("🚀 إطلاق رندر الإنجاز النهائي (V92)"):
    try:
        status = st.info("⏳ جاري تأمين الملفات وبناء الجدول الزمني للمشاهد...")
        
        # [معالجة الصوت]
        audio_p = os.path.join(ASSETS_DIR, "v92_voice.mp3")
        if u_voice:
            with open(audio_p, "wb") as f: f.write(u_voice.getbuffer())
        else:
            gTTS(ai_text, lang='ar').save(audio_p)
        voice = AudioFileClip(audio_p)

        # [تقسيم المشاهد]
        sentences = [s.strip() for s in re.split(r'[.؟!،]+', ai_text) if len(s.strip()) > 1]
        dur_scene = voice.duration / len(sentences)
        h = 1080; w = int(h*9/16) if "9:16" in dim else int(h*16/9)
        
        img_clips = []
        sub_clips = []

        # [ Image of a synchronous processing flow where each asset is verified before being added to a render queue ]
        # [تجهيز المشاهد مع التحقق من الوجود الفعلي]
        for i, sent in enumerate(sentences):
            p = os.path.join(ASSETS_DIR, f"v92_img_{i}.jpg")
            
            # ضمان وجود الصورة (سواء تحميل أو توليد بديل)
            if img_mode == "أوتوماتيك":
                get_guaranteed_image(sent, p, (w, h), i)
            elif u_imgs:
                with open(p, "wb") as f: f.write(u_imgs[i % len(u_imgs)].getbuffer())
            
            # فحص أخير قبل الاستدعاء
            if os.path.exists(p):
                # تأثير الزووم 1، 5
                c = ImageClip(p).with_duration(dur_scene).crossfadein(0.5)
                z_factor = 1.18 if i % 2 == 0 else 0.82
                c = c.resized(lambda t: 1 + (z_factor-1) * (t / dur_scene))
                img_clips.append(c)
                sub_clips.append(create_subtitle((w, h), sent, i*dur_scene, dur_scene))

        # دمج المشاهد
        video_track = concatenate_videoclips(img_clips, method="compose")

        # الهوية 9
        overlay = []
        if logo_file:
            logo_p = os.path.join(ASSETS_DIR, "v92_logo.png")
            Image.open(logo_file).convert("RGBA").resize((w//6, w//6)).save(logo_p)
            overlay.append(ImageClip(logo_p).with_duration(voice.duration).with_position(("right", "top")))

        # الرندر النهائي
        final = CompositeVideoClip([video_track] + overlay + sub_clips, size=(w, h)).with_audio(voice)
        out_f = os.path.join(VIDEOS_DIR, "Mediawy_V92_Final.mp4")
        final.write_videofile(out_f, fps=24, codec="libx264")
        st.video(out_f)

    except Exception as e:
        st.error(f"⚠️ خطأ فني في الرندر: {str(e)}")
