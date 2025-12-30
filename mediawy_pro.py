import streamlit as st
import os, requests, re, io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import moviepy as mp
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip

# ضبط محرك الصور للسيرفر
if os.name == 'posix': os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"

# 11- فواصل المجلدات
MEDIA_DIR = "Mediawy_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- 4. محرك الصور السياقي (أوتوماتيك) ---
def get_verified_image(query, path, size, index):
    w, h = size
    # استخراج كلمات مفتاحية ذكية لضمان الارتباط بالمحتوى
    clean_q = "+".join(re.findall(r'\w+', query)[:2])
    url = f"https://source.unsplash.com/featured/{w}x{h}/?{clean_q},{index}"
    try:
        resp = requests.get(url, timeout=10)
        img = Image.open(io.BytesIO(resp.content)).convert("RGB").resize(size)
        img.save(path, "JPEG")
        return True
    except:
        # البديل السريع
        img = Image.new("RGB", size, (index*30%255, 40, 80))
        img.save(path, "JPEG")
        return True

# --- 1, 5. محرك الزووم والنقلات الناعمة ---
def apply_pro_zoom(clip, index):
    dur = clip.duration
    # زووم ناعم (Ken Burns Effect)
    if index % 2 == 0:
        return clip.resized(lambda t: 1 + 0.18 * (t / dur))
    else:
        return clip.resized(lambda t: 1.18 - 0.18 * (t / dur))

# --- 7. محرك نصوص Clipchamp (كلمة بكلمة) ---
def create_subtitle(size, text, start_t, dur):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    f_size = size[0] // 16
    try: font = ImageFont.truetype("arial.ttf", f_size)
    except: font = ImageFont.load_default()
    
    # حساب أبعاد الصندوق
    tw = len(text) * (f_size * 0.65)
    th = f_size * 1.3
    y_pos = int(size[1] * 0.72) # الثلث الأخير
    x_pos = (size[0] // 2) - (int(tw) // 2)
    
    # خلفية النص الصفراء/السوداء الاحترافية
    draw.rectangle([x_pos-20, y_pos-10, x_pos+tw+20, y_pos+th+10], fill=(0,0,0,190))
    draw.text((x_pos, y_pos), text, font=font, fill="yellow")
    return ImageClip(np.array(img)).with_start(start_t).with_duration(dur)

# --- واجهة المستخدم (تطبيق الـ 11 إضافة حرفياً) ---
st.set_page_config(page_title="Mediawy V74", layout="wide")
st.markdown("<h1 style='text-align:center; color:red;'>🎬 Mediawy Studio V74</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ الدستور الملياري")
    # 2- الأبعاد
    dim = st.selectbox("📏 2- الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    # 1- نمط المونتاج
    edit_style = st.selectbox("🎭 1- النمط:", ["سينمائي", "درامي", "وثائقي"])
    st.divider() # 11- فواصل

    # 3- الصوت (AI, البشرى، ElevenLabs بـ 3 مربعات)
    st.subheader("🎙️ 3- هندسة الصوت")
    audio_src = st.radio("المصدر:", ["AI (GTTS)", "ElevenLabs 💎", "بشري 🎤"])
    if audio_src == "ElevenLabs 💎":
        st.text_input("📦 1- API Key", type="password")
        st.text_input("📦 2- Voice ID")
        st.info("📦 3- النص في المربع بالأسفل")
    ai_text = st.text_area("✍️ النص (حتى 500 كلمة):", value="النجاح لا يأتي بالصدفة. إنه نتيجة العمل الجاد والإرادة.")
    st.divider()

    # 4- الصور
    st.subheader("🖼️ 4- الصور (أوتوماتيك/رفع)")
    img_mode = st.radio("الجلب:", ["أوتوماتيك (سياقي)", "رفع يدوي"])
    user_imgs = st.file_uploader("ارفع صورك (حتى 500)", accept_multiple_files=True)
    st.divider()

    # 6- الموسيقى
    st.subheader("🎵 6- موسيقى خلفية")
    bg_music = st.toggle("تفعيل الموسيقى الاختيارية", value=True)
    st.divider()

    # 8, 9- الهوية
    show_banner = st.toggle("8- بنر سفلي متحرك", value=True)
    logo_file = st.file_uploader("9- اللوجو")

# --- محرك الرندر الملياري ---
if st.button("🚀 إطلاق خط الإنتاج المصلح"):
    try:
        status = st.info("⏳ جاري المونتاج... تحليل السياق... تفعيل الزووم الحقيقي...")
        
        # [الصوت]
        audio_path = os.path.join(ASSETS_DIR, "v.mp3")
        gTTS(ai_text, lang='ar').save(audio_path)
        voice = AudioFileClip(audio_path)
        total_dur = voice.duration
        
        # [تحليل الجمل]
        sentences = [s.strip() for s in re.split(r'[.؟!،]+', ai_text) if len(s.strip()) > 1]
        if not sentences: sentences = ["Mediawy Studio"]
        dur_per_scene = total_dur / len(sentences)

        # [بناء المشاهد]
