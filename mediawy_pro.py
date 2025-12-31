import streamlit as st
import os, requests, re, io, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip, vfx

# --- 1. إعداد المجلدات ---
MEDIA_DIR = "Mediawy_White_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- محرك الصور الضامن ---
def get_guaranteed_image(query, path, size):
    w, h = size
    q = "+".join(re.findall(r'\w+', query)[:3])
    # استخدام Picsum كمصدر مستقر جداً للرندرات السريعة
    url = f"https://picsum.photos/seed/{random.randint(1,1000)}/{w}/{h}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            img = Image.open(io.BytesIO(resp.content)).convert("RGB").resize(size)
            img.save(path, "JPEG")
            return True
    except:
        pass
    # صورة طوارئ بيضاء شيك
    img = Image.new("RGB", size, (240, 240, 240))
    img.save(path, "JPEG")
    return True

# --- تصميم الواجهة (الخلفية البيضاء والتقسيم الثلاثي) ---
st.set_page_config(page_title="Mediawy V105 Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333333; }
    [data-testid="stSidebar"] { background-color: #F8F9FA; border-right: 1px solid #dee2e6; }
    .render-box { border: 2px solid #007BFF; padding: 20px; border-radius: 15px; background: #F8F9FA; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    h2 { color: #007BFF !important; border-bottom: 2px solid #007BFF; }
    .stButton>button { background-color: #007BFF; color: white; border-radius: 8px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#007BFF;'>🎬 Mediawy Studio V105 - White Edition</h1>", unsafe_allow_html=True)

# تقسيم الواجهة (الجانبين والمنتصف)
col_right, col_mid, col_left = st.columns([1, 1.8, 1])

# --- الجانب الأيمن: الأبعاد والصوت ---
with col_right:
    st.markdown("## 📏 1. الأبعاد")
    platform = st.selectbox("المقاس:", ["Shorts/TikTok (9:16)", "YouTube (16:9)", "Facebook (1:1)"])
    st.divider()

    st.markdown("## 🎙️ 2. هندسة الصوت")
    v_src = st.radio("المصدر:", ["AI 🤖", "ElevenLabs 💎", "بشري 🎤"])
    
    voice_text = ""
    if v_src == "AI 🤖":
        voice_text = st.text_area("✍️ جدول النص (AI):")
    elif v_src == "ElevenLabs 💎":
        el_key = st.text_input("🔑 API Key:")
        el_model = st.text_input("📦 Model ID:")
        voice_text = st.text_area("✍️ نص ElevenLabs:")
    else:
        u_voice = st.file_uploader("📥 أيقونة تحميل الصوت البشري:")
        voice_text = st.text_area("✍️ النص (للمزامنة):")

# --- الجانب الأيسر: الصور والنمط والهوية ---
with col_left:
    st.markdown("## 🎭 3. نمط المونتاج")
    m_style = st.selectbox("النمط:", ["سينمائي 🎬", "درامي 🎭", "وثائقي 🎞️"])
    st.divider()

    st.markdown("## 🖼️ 4. محرك الصور")
    img_opt = st.radio("الجلب:", ["أوتوماتيك 🤖", "يدوي 📁"])
    if img_opt == "يدوي 📁":
        u_imgs = st.file_uploader("📁 أيقونة تحميل الصور:", accept_multiple_files=True)
    else:
        keywords = st.text_input("🔍 مربع الكلمات المفتاحية:")
    st.divider()

    st.markdown("## 🎨 5. الهوية")
    show_subs = st.toggle("ترجمة كلمة بكلمة", value=True)
    use_logo = st.toggle("إضافة لوجو")
    u_logo = st.file_uploader("🖼️ أيقونة تحميل اللوجو:") if use_logo else None

# --- العمود الأوسط: الإنتاج والـ SEO ---
with col_mid:
    st.markdown("<div class='render-box'>", unsafe_allow_html=True)
    st.subheader("📺 شاشة الإنتاج المركزي")
    
    [Image of a professional video editing timeline showing layered audio tracks for voice and background music, contextual video clips with zoom indicators, and overlay tracks for logos and subtitles]

    if st.button("🚀 بدء الرندر (V105)"):
        if not voice_text:
            st.error("أدخل النص أولاً يا برنس!")
        else:
            try:
                with st.spinner("جاري معالجة الـ 11 إضافة
