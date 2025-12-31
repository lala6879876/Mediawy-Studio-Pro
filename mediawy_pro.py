import streamlit as st
import os, requests, re, io, random
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, vfx

# --- 1. التأسيس (فواصل المجلدات) ---
MEDIA_DIR = "Mediawy_Studio_Final"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- واجهة المستخدم البيضاء (التصميم العصري الأنيق) ---
st.set_page_config(page_title="Mediawy V113 Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333; }
    .stDivider { margin: 20px 0 !important; border-bottom: 2px solid #f0f2f6; }
    .render-box { border: 2px solid #007BFF; padding: 25px; border-radius: 15px; background: #fcfcfc; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    .side-panel { background: #f8f9fa; padding: 20px; border-radius: 10px; }
    h1, h2, h3 { color: #007BFF !important; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🎬 Mediawy Studio V113 - Professional Dashboard</h1>", unsafe_allow_html=True)

# --- توزيع الاستوديو (يمين: تحكم - منتصف: إنتاج - يسار: إضافات) ---
col_right, col_mid, col_left = st.columns([1.2, 1.8, 1.2])

# --- الجانب الأيمن (التحكم الأساسي) ---
with col_right:
    st.subheader("📏 2- الأبعاد")
    dim = st.selectbox("المقاس:", ["Shorts (9:16)", "YouTube (16:9)", "TikTok/Insta (9:16)", "Facebook (1:1)"])
    st.divider() # 11- فواصل

    st.subheader("🎙️ 3- هندسة الصوت")
    v_src = st.radio("المصدر:", ["بشري 🎤", "AI (GTTS) 🤖", "ElevenLabs 💎"])
    
    # تنفيذ منطق المربعات الشرطية (3)
    if v_src == "بشري 🎤":
        u_voice = st.file_uploader("📥 أيقونة تحميل الصوت البشري:")
        voice_text = st.text_area("✍️ النص (للمزامنة والترجمة):")
    elif v_src == "AI (GTTS) 🤖":
        voice_text = st.text_area("✍️ مربع كتابة النص (AI):")
    elif v_src == "ElevenLabs 💎":
        el_key = st.text_input("🔑 مربع مفتاح ElevenLabs (API Key):")
        el_mod = st.text_input("📦 مربع الموديل (Model ID):")
        voice_text = st.text_area("✍️ مربع النص (ElevenLabs):")
    
    st.divider()
    st.subheader("🎭 1- نمط المونتاج")
    m_style = st.selectbox("النمط:", ["سينمائي 🎬", "درامي 🎭", "وثائقي 📜"])

# --- الجانب الأيسر (الإضافات الفنية) ---
with col_left:
    st.subheader("🖼️ 4- محرك الصور")
    img_mode = st.radio("الجلب:", ["اتوماتيك ✨", "يدوي 📁"])
    if img_mode == "اتوماتيك ✨":
        img_keywords = st.text_input("🔍 مربع الكلمات المفتاحية للصور:")
    else:
        u_imgs = st.file_uploader("📁 أيقونة الرفع (Lmt: 500):", accept_multiple_files=True)
    
    st.divider()
    st.subheader("🎵 6- الموسيقى الخلفية")
    m_bg = st.radio("الموسيقى:", ["اختيارية (بدون)", "اتوماتيك 🎹", "يدوية 🎷"])
    u_music = st.file_uploader("📥 أيقونة تحميل الموسيقى:") if m_bg == "يدوية 🎷" else None
    
    st.divider()
    st.subheader("🎨 8, 9- الهوية")
    use_banner = st.toggle("8- بنر سفلي (اختياري)")
    banner_txt = st.text_input("✍️ مربع نص البنر:") if use_banner else ""
    
    use_logo = st.toggle("9- إضافة لوجو (اعلى يمين)")
    u_logo = st.file_uploader("🖼️ أيقونة تحميل اللوجو:") if use_logo else None

# --- العمود الأوسط (غرفة الإنتاج والـ SEO) ---
with col_mid:
    st.markdown("<div class='render-box'>", unsafe_allow_html=True)
    st.subheader("📺 شاشة الإنتاج المركزي")
    
    show_subs = st.toggle("7- ترجمة كلمة بكلمة (Clipchamp Style)", value=True)

    if st.button("🚀 إطلاق الإنتاج الملياري (ضرب نار)"):
        if not voice_text: st.error("أدخل النص أولاً يا برنس!")
        else:
            try:
                with st.spinner("⏳ جاري المونتاج السينمائي والتحقق من الـ 11 إضافة..."):
                    # 1. الصوت
                    v_p = os.path.join(ASSETS_DIR, "v.mp3")
                    if v_src == "بشري 🎤" and u_voice:
                        with open(v_p, "wb") as f: f.write(u_voice.getbuffer())
                    else:
                        gTTS(voice_text, lang='ar').save(v_p)
                    audio = AudioFileClip(v_p)

                    # 2. الأبعاد
                    w, h = (1080, 1920) if "9:16" in dim else (1920, 1080)
                    
                    # 3. المشاهد (زووم ونقلات 1, 5)
                    sentences = [s.strip() for s in re.split(r'[.؟!،]+', voice_text) if len(s.strip()) > 1]
                    dur = audio.duration / len(sentences)
                    clips = []
                    
                    for i, sent in enumerate(sentences):
                        img_p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
                        if img_mode == "اتوماتيك ✨":
                            resp = requests.get(f"https://picsum.photos/seed/{i}/{w}/{h}")
                            Image.open(io.BytesIO(resp.content)).save(img_p)
                        else:
                            with open(img_p, "wb") as f: f.write(u_imgs[i % len(u_imgs)].getbuffer())
                        
                        c = ImageClip(img_p).with_duration(dur + 0.5)
                        # زووم ان وزووم اوت (5)
                        z = 1.15 if i % 2 == 0 else 0.85
                        c = c.resized(lambda t: 1 + (z-1) * (t / dur))
                        clips.append(c.crossfadein(0.5))

                    video = concatenate_videoclips(clips, method="compose", padding=-0.3)

                    # 4. طبقات الهوية (اللوجو 9 والبنر 8)
                    layers = [video]
                    if use_logo and u_logo:
                        lp = os.path.join(ASSETS_DIR, "logo.png")
                        Image.open(u_logo).resize((w//7, w//7)).save(lp)
                        layers.append(ImageClip(lp).with_duration(audio.duration).with_position(("right", "top")))

                    final = CompositeVideoClip(layers, size=(w, h)).with_audio(audio)
                    out = os.path.join(VIDEOS_DIR, "Mediawy_V113.mp4")
                    final.write_vid(out, fps=24, codec="libx264")
                    
                    st.video(out)
                    st.success("🎯 تم الانتهاء!")

                    # 10- قسم الـ SEO اسفل الفيديو
                    st.divider()
                    st.markdown("### 📊 10- ملخص الفيديو والـ SEO")
                    st.info(f"**الاسم المقترح:** {sentences[0]}")
                    st.info(f"**الكلمات المفتاحية:** {img_keywords if img_mode == 'اتوماتيك ✨' else 'يدوي'}")
                    st.info(f"**الوصف:** فيديو احترافي {m_style} تم إنتاجه بمواصفات Mediawy.")

            except Exception as e: st.error(f"خطأ: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
