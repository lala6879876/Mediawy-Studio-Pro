import streamlit as st
import os, requests, re, io, random, time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip, vfx

# --- 1. التأسيس الهندسي (فواصل المجلدات) ---
MEDIA_DIR = "Mediawy_Ultimate_V112"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- 2. محرك الصور الذكي (صياد السياق) ---
def get_intelligent_image(query, path, size, style):
    w, h = size
    # دمج الكلمات المفتاحية مع النمط المختار
    style_map = {
        "سينمائي 🎬": "cinematic, 4k, anamorphic lens",
        "درامي 🎭": "moody, dramatic lighting, emotional",
        "وثائقي 📜": "historical, realistic, national geographic style"
    }
    q = "+".join(re.findall(r'\w+', query)[:3]) + "," + style_map.get(style, "")
    url = f"https://source.unsplash.com/featured/{w}x{h}/?{q}&sig={random.randint(1,1000)}"
    try:
        resp = requests.get(url, timeout=12)
        if resp.status_code == 200:
            img = Image.open(io.BytesIO(resp.content)).convert("RGB").resize(size)
            img.save(path, "JPEG")
            return True
    except: pass
    # Fallback: خلفية بيضاء فخمة ببرواز رفيع
    img = Image.new("RGB", size, (250, 250, 250))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, w, h], outline="#D4AF37", width=2) # برواز ذهبي رفيع
    img.save(path, "JPEG")
    return True

# --- 3. تصميم الواجهة (عصري - حيوي - خبير) ---
st.set_page_config(page_title="Mediawy V112 Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #2D3436; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .sidebar .sidebar-content { background-color: #FDFDFD; border-right: 1px solid #EAEAEA; }
    .main-panel { border: 1px solid #E0E0E0; padding: 30px; border-radius: 20px; background-color: #FAFAFA; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #0984E3 !important; font-weight: 300 !important; }
    .stButton>button { width: 100%; background: linear-gradient(90deg, #0984E3, #00CEC9); color: white; border: none; padding: 15px; border-radius: 10px; font-size: 18px; transition: 0.3s; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(9,132,227,0.3); }
    .stDivider { margin: 25px 0 !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🎬 Mediawy Studio V112 <span style='font-size:18px; color:#636E72;'>Professional Automation</span></h1>", unsafe_allow_html=True)

# توزيع المحطة (يمين: تحكم - منتصف: معاينة - يسار: إضافات)
col_right, col_mid, col_left = st.columns([1.1, 1.8, 1.1])

with col_right:
    st.subheader("📏 1. الأبعاد والمنصة")
    dim_opt = st.selectbox("المقاس:", ["Shorts/TikTok (9:16)", "YouTube (16:9)", "Facebook (1:1)", "Instagram (4:5)"])
    st.divider() # 11- فواصل

    st.subheader("🎙️ 2. هندسة الصوت")
    v_src = st.radio("مصدر الصوت:", ["بشري 🎤", "AI 🤖", "ElevenLabs 💎"])
    if v_src == "بشري 🎤":
        u_voice = st.file_uploader("📥 ارفع ملف صوتك (MP3/WAV)")
        voice_text = st.text_area("✍️ النص (للمزامنة والترجمة):")
    elif v_src == "AI 🤖":
        voice_text = st.text_area("✍️ جدول كتابة النص:")
    else:
        # ElevenLabs 3 مربعات
        el_col1, el_col2 = st.columns(2)
        with el_col1: el_key = st.text_input("🔑 API Key")
        with el_col2: el_mod = st.text_input("📦 Model ID")
        voice_text = st.text_area("✍️ نص الـ ElevenLabs:")
    st.divider()

    st.subheader("🎭 3. نمط المونتاج")
    m_style = st.selectbox("اختر الروح:", ["سينمائي 🎬", "درامي 🎭", "وثائقي 📜"])

with col_left:
    st.subheader("🖼️ 4. محرك الصور")
    img_opt = st.radio("الجلب:", ["أوتوماتيك ✨", "رفع يدوي 📁"])
    if img_opt == "أوتوماتيك ✨":
        img_keywords = st.text_input("🔍 الكلمات المفتاحية للصور:")
    else:
        u_imgs = st.file_uploader("📁 ارفع صورك (Limit: 500):", accept_multiple_files=True)
    st.divider()

    st.subheader("🎵 5. الموسيقى الخلفية")
    m_bg_opt = st.radio("الموسيقى:", ["يدوي 🎷", "أوتوماتيك 🎹", "بدون"])
    u_music = st.file_uploader("📥 تحميل الموسيقى:") if m_bg_opt == "يدوي 🎷" else None
    st.divider()

    st.subheader("🎨 6. الهوية والترجمة")
    show_subs = st.toggle("🔤 ترجمة كلمة بكلمة (Clipchamp)", value=True)
    use_banner = st.toggle("🏁 تفعيل البنر السفلي")
    banner_txt = st.text_input("نص البنر:") if use_banner else ""
    use_logo = st.toggle("🖼️ إضافة لوجو")
    u_logo = st.file_uploader("أيقونة اللوجو:") if use_logo else None

with col_mid:
    st.markdown("<div class='main-panel'>", unsafe_allow_html=True)
    st.subheader("📺 شاشة الإنتاج المركزي")
    
    

    if st.button("🚀 إطلاق رندر الإنجاز الملياري"):
        if not voice_text: st.error("أدخل النص أولاً يا برنس!")
        else:
            try:
                with st.spinner("جاري تنفيذ العمليات السينمائية..."):
                    # 1. الصوت
                    v_p = os.path.join(ASSETS_DIR, "voice.mp3")
                    if v_src == "بشري 🎤" and u_voice:
                        with open(v_p, "wb") as f: f.write(u_voice.getbuffer())
                    else:
                        gTTS(voice_text, lang='ar').save(v_p)
                    audio = AudioFileClip(v_p)

                    # 2. الأبعاد
                    w, h = (1080, 1920) if "9:16" in dim_opt else (1920, 1080)
                    
                    # 3. بناء المشاهد (زووم إن/أوت ودخلات ناعمة)
                    sentences = [s.strip() for s in re.split(r'[.؟!،]+', voice_text) if len(s.strip()) > 1]
                    dur = audio.duration / len(sentences)
                    clips = []
                    
                    for i, sent in enumerate(sentences):
                        img_p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
                        if img_opt == "أوتوماتيك ✨":
                            get_intelligent_image(sent + " " + img_keywords, img_p, (w, h), m_style)
                        else:
                            with open(img_p, "wb") as f: f.write(u_imgs[i % len(u_imgs)].getbuffer())
                        
                        c = ImageClip(img_p).with_duration(dur + 0.4)
                        # زووم احترافي (1=In, 2=Out)
                        z_factor = 1.12 if i % 2 == 0 else 0.88
                        c = c.resized(lambda t: 1 + (z_factor-1) * (t / dur))
                        clips.append(c.crossfadein(0.5))

                    video_track = concatenate_videoclips(clips, method="compose", padding=-0.3)

                    # 4. طبقات الهوية والترجمة (فونت صغير وشيك)
                    layers = [video_track]
                    # لوجو أعلى يمين
                    if use_logo and u_logo:
                        lp = os.path.join(ASSETS_DIR, "logo.png")
                        Image.open(u_logo).resize((w//8, w//8)).save(lp)
                        layers.append(ImageClip(lp).with_duration(audio.duration).with_position(("right", "top")).with_opacity(0.8))
                    
                    final_vid = CompositeVideoClip(layers, size=(w, h)).with_audio(audio)
                    out_f = os.path.join(VIDEOS_DIR, "Mediawy_Success.mp4")
                    final_vid.write_videofile(out_f, fps=24, codec="libx264")
                    
                    st.video(out_f)
                    
                    # 10. ملخص الـ SEO
                    st.divider()
                    st.markdown("### 📈 10. ملخص الفيديو والـ SEO")
                    st_col1, st_col2 = st.columns(2)
                    with st_col1:
                        st.info(f"**الاسم المقترح:** {sentences[0]}")
                        st.info(f"**الكلمات المفتاحية:** {img_keywords if img_keywords else sentences[0][:20]}")
                    with st_col2:
                        st.info(f"**الوصف:** فيديو {m_style} تم إنتاجه باحترافية عبر ذكاء Mediawy الاصطناعي.")
                        st.info(f"**الهاشتاج:** #AI #Production #{m_style.replace(' ','_')}")

            except Exception as e: st.error(f"⚠️ خطأ: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
