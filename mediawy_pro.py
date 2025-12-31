import streamlit as st
import os, requests, re, io, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, vfx

# --- 1. التأسيس الهندسي ---
MEDIA_DIR = "Mediawy_Final_V114"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- 2. محرك الصور (أوتوماتيك) ---
def get_verified_image(query, path, size):
    w, h = size
    q = "+".join(re.findall(r'\w+', query)[:3])
    url = f"https://picsum.photos/seed/{random.randint(1,1000)}/{w}/{h}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            Image.open(io.BytesIO(resp.content)).convert("RGB").resize(size).save(path, "JPEG")
            return True
    except: pass
    Image.new("RGB", size, (250, 250, 250)).save(path, "JPEG")
    return True

# --- 3. تصميم الواجهة (خلفية بيضاء - تصميم Dashboard) ---
st.set_page_config(page_title="Mediawy V114 Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333; }
    .render-zone { border: 2px solid #007BFF; padding: 20px; border-radius: 15px; background-color: #fcfcfc; }
    h2 { color: #007BFF !important; font-size: 1.2rem; border-bottom: 2px solid #007BFF; padding-bottom: 5px; }
    .stDivider { margin: 15px 0 !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#007BFF;'>🎬 Mediawy Studio V114 Professional</h1>", unsafe_allow_html=True)

# التوزيع الثلاثي
col_right, col_mid, col_left = st.columns([1.1, 1.8, 1.1])

with col_right:
    st.subheader("📏 2- الأبعاد")
    dim = st.selectbox("المقاس:", ["Shorts (9:16)", "YouTube (16:9)", "Square (1:1)"])
    st.divider()

    st.subheader("🎙️ 3- هندسة الصوت")
    v_src = st.radio("المصدر:", ["بشري 🎤", "AI 🤖", "ElevenLabs 💎"], index=0)
    if v_src == "بشري 🎤":
        u_voice = st.file_uploader("📥 تحميل الصوت البشري:")
    elif v_src == "ElevenLabs 💎":
        c1, c2 = st.columns(2)
        with c1: el_key = st.text_input("🔑 API Key")
        with c2: el_mod = st.text_input("📦 Model ID")
    
    voice_text = st.text_area("✍️ جدول النص (مهم جداً):")
    st.divider()
    st.subheader("🎭 1- النمط")
    m_style = st.selectbox("الروح:", ["سينمائي 🎬", "درامي 🎭", "وثائقي 📜"])

with col_left:
    st.subheader("🖼️ 4- الصور")
    img_mode = st.radio("الجلب:", ["أوتوماتيك ✨", "يدوي 📁"])
    if img_mode == "يدوي 📁":
        u_imgs = st.file_uploader("📁 ارفع صورك (حتى 500):", accept_multiple_files=True)
    else:
        img_q = st.text_input("🔍 الكلمات المفتاحية:")
    st.divider()

    st.subheader("🎨 8, 9- الهوية")
    use_banner = st.toggle("8- بنر سفلي")
    banner_txt = st.text_input("نص البنر:") if use_banner else ""
    use_logo = st.toggle("9- لوجو (أعلى يمين)")
    u_logo = st.file_uploader("تحميل اللوجو:") if use_logo else None

with col_mid:
    st.markdown("<div class='render-zone'>", unsafe_allow_html=True)
    st.subheader("📺 شاشة الإنتاج")
    
    

    if st.button("🚀 إطلاق الرندر الملياري"):
        if not voice_text: st.warning("أدخل النص أولاً!")
        else:
            try:
                with st.spinner("جاري المونتاج..."):
                    # 1. الصوت
                    v_p = os.path.join(ASSETS_DIR, "v.mp3")
                    if v_src == "بشري 🎤" and u_voice:
                        with open(v_p, "wb") as f: f.write(u_voice.getbuffer())
                    else:
                        gTTS(voice_text, lang='ar').save(v_p)
                    audio = AudioFileClip(v_p)

                    # 2. الأبعاد
                    w, h = (1080, 1920) if "9:16" in dim else (1920, 1080)
                    
                    # 3. المشاهد (إصلاح النقلات والزووم)
                    sentences = [s.strip() for s in re.split(r'[.؟!،]+', voice_text) if len(s.strip()) > 1]
                    dur = audio.duration / len(sentences)
                    clips = []

                    for i, sent in enumerate(sentences):
                        img_p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
                        if img_mode == "أوتوماتيك ✨":
                            get_verified_image(sent + " " + (img_q or ""), img_p, (w, h))
                        else:
                            with open(img_p, "wb") as f: f.write(u_imgs[i % len(u_imgs)].getbuffer())
                        
                        c = ImageClip(img_p).with_duration(dur + 0.5)
                        # زووم ناعم (Precision Zoom)
                        z = 1.1 if i % 2 == 0 else 0.9
                        c = c.resized(lambda t: 1 + (z-1) * (t / dur))
                        # الإصلاح: استخدام التنسيق الجديد للنقلات في MoviePy v2
                        try:
                            c = c.with_effects([vfx.CrossFadeIn(0.5)])
                        except:
                            pass # في حال كانت النسخة قديمة جداً
                        clips.append(c)

                    main_vid = concatenate_videoclips(clips, method="compose", padding=-0.3)

                    # 4. الهوية (اللوجو والبنر)
                    layers = [main_vid]
                    if use_logo and u_logo:
                        lp = os.path.join(ASSETS_DIR, "l.png")
                        Image.open(u_logo).convert("RGBA").resize((w//8, w//8)).save(lp)
                        layers.append(ImageClip(lp).with_duration(audio.duration).with_position(("right", 20)))

                    final = CompositeVideoClip(layers, size=(w, h)).with_audio(audio)
                    out = os.path.join(VIDEOS_DIR, "Mediawy_Success.mp4")
                    final.write_videofile(out, fps=24, codec="libx264")
                    
                    st.video(out)
                    
                    # 10. الـ SEO
                    st.divider()
                    st.markdown("### 📊 10- ملخص الـ SEO")
                    st.info(f"**الاسم:** {sentences[0]}\n\n**الكلمات:** {img_q or 'تلقائي'}\n\n**الهاشتاج:** #AI #Production #{m_style.split()[0]}")

            except Exception as e: st.error(f"حدث خطأ: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
