import streamlit as st
import os, requests, re, io, random
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, vfx

# --- 1. التأسيس (تنظيف المجلدات) ---
MEDIA_DIR = "Mediawy_V116"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- واجهة بيضاء وتصميم Dashboard احترافي ---
st.set_page_config(page_title="Mediawy V116", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333; }
    .side-box { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 1px solid #E0E0E0; }
    .render-box { border: 2px solid #007BFF; padding: 25px; border-radius: 15px; background-color: #FAFAFA; }
    h2, h3 { color: #007BFF !important; font-size: 1.1rem !important; }
    .stDivider { margin: 15px 0 !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#007BFF;'>🎬 Mediawy Studio V116 - Professional</h1>", unsafe_allow_html=True)

# التوزيع الثلاثي (يمين: تحكم - منتصف: إنتاج - يسار: هوية)
col_right, col_mid, col_left = st.columns([1.1, 1.8, 1.1])

with col_right:
    st.subheader("📏 2- الأبعاد")
    dim = st.selectbox("المقاس:", ["Shorts (9:16)", "YouTube (16:9)", "TikTok (9:16)", "Post (1:1)"])
    st.divider()

    st.subheader("🎙️ 3- هندسة الصوت")
    v_src = st.radio("المصدر:", ["بشري 🎤", "AI 🤖", "ElevenLabs 💎"], index=0)
    
    # تنفيذ منطق المربعات الشرطية (3)
    if v_src == "بشري 🎤":
        u_voice = st.file_uploader("📥 أيقونة تحميل الصوت البشري:")
        voice_text = st.text_area("✍️ النص (اختياري للترجمة):")
    elif v_src == "AI 🤖":
        voice_text = st.text_area("✍️ مربع كتابة النص:")
    elif v_src == "ElevenLabs 💎":
        el_key = st.text_input("🔑 API Key")
        el_mod = st.text_input("📦 Model ID")
        voice_text = st.text_area("✍️ نص ElevenLabs:")
    st.divider()
    
    st.subheader("🎭 1- النمط")
    m_style = st.selectbox("النمط:", ["سينمائي 🎬", "درامي 🎭", "وثائقي 📜"])

with col_left:
    st.subheader("🖼️ 4- الصور")
    img_mode = st.radio("الجلب:", ["أوتوماتيك ✨", "يدوي 📁"])
    if img_mode == "يدوي 📁":
        u_imgs = st.file_uploader("📁 أيقونة الرفع (حتى 500):", accept_multiple_files=True)
    else:
        img_q = st.text_input("🔍 مربع الكلمات المفتاحية:")
    st.divider()

    st.subheader("🎨 8, 9- الهوية")
    use_logo = st.toggle("9- إضافة لوجو (أعلى يمين)")
    u_logo = st.file_uploader("🖼️ تحميل اللوجو:") if use_logo else None
    
    use_banner = st.toggle("8- بنر سفلي")
    banner_txt = st.text_input("✍️ نص البنر:") if use_banner else ""

with col_mid:
    st.markdown("<div class='render-box'>", unsafe_allow_html=True)
    st.subheader("📺 شاشة الإنتاج المركزي")
    
    show_subs = st.toggle("7- ترجمة كلمة بكلمة", value=True)

    if st.button("🚀 إطلاق رندر الإنجاز (V116)"):
        # فحص الشروط بدون تعقيد
        if v_src == "بشري 🎤" and not u_voice:
            st.error("ارفع ملف الصوت البشري أولاً!")
        else:
            try:
                with st.spinner("⏳ جاري المونتاج..."):
                    # 1. الصوت
                    v_p = os.path.join(ASSETS_DIR, "v.mp3")
                    if v_src == "بشري 🎤":
                        with open(v_p, "wb") as f: f.write(u_voice.getbuffer())
                    else:
                        gTTS(voice_text, lang='ar').save(v_p)
                    audio = AudioFileClip(v_p)

                    # 2. الأبعاد
                    w, h = (1080, 1920) if "9:16" in dim else (1920, 1080)
                    
                    # 3. بناء المشاهد (1, 5) زووم ونقلات
                    num_scenes = 5 # افتراضي
                    dur = audio.duration / num_scenes
                    clips = []
                    
                    

                    for i in range(num_scenes):
                        img_p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
                        if img_mode == "أوتوماتيك ✨":
                            resp = requests.get(f"https://picsum.photos/seed/{i}/{w}/{h}")
                            Image.open(io.BytesIO(resp.content)).save(img_p)
                        else:
                            with open(img_p, "wb") as f: f.write(u_imgs[i % len(u_imgs)].getbuffer())
                        
                        c = ImageClip(img_p).set_duration(dur + 0.5)
                        # زووم ناعم (5)
                        z = 1.1 if i % 2 == 0 else 0.9
                        c = c.resize(lambda t: 1 + (z-1) * (t / dur))
                        clips.append(c.crossfadein(0.5))

                    video = concatenate_videoclips(clips, method="compose", padding=-0.3)

                    # 4. طبقات الهوية (8, 9)
                    layers = [video]
                    if use_logo and u_logo:
                        lp = os.path.join(ASSETS_DIR, "l.png")
                        Image.open(u_logo).resize((w//8, w//8)).save(lp)
                        layers.append(ImageClip(lp).set_duration(audio.duration).set_position(("right", 20)))

                    final = CompositeVideoClip(layers, size=(w, h)).set_audio(audio)
                    out = os.path.join(VIDEOS_DIR, "Mediawy_Success.mp4")
                    final.write_videofile(out, fps=24, codec="libx264")
                    
                    st.video(out)
                    st.success("🎯 تم الرندر بنجاح!")

                    # 10. الـ SEO
                    st.divider()
                    st.markdown("### 📊 10- ملخص الـ SEO")
                    st.info(f"**الاسم:** {img_q if img_q else 'فيديو احترافي'}\n\n**الكلمات:** {img_q}\n\n**الهاشتاج:** #AI #Production")

            except Exception as e: st.error(f"حدث خطأ: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
