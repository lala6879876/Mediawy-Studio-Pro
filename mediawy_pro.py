import streamlit as st
import os, requests, re, io, random
from PIL import Image
from gtts import gTTS

# محرك المونتاج (توافق شامل V1 & V2)
try:
    from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, vfx
except ImportError:
    from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, vfx

# --- 1. إعداد البيئة ---
MEDIA_DIR = "Mediawy_Studio_V124"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- واجهة Dashboard بيضاء ومنظمة ---
st.set_page_config(page_title="Mediawy V124 Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333; font-size: 14px; }
    .render-zone { border: 2px solid #007BFF; padding: 20px; border-radius: 15px; background-color: #fcfcfc; }
    h2, h3 { color: #007BFF !important; font-size: 0.95rem !important; font-weight: bold; }
    .stDivider { margin: 10px 0 !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#007BFF; font-size:26px;'>🎬 Mediawy Studio V124</h1>", unsafe_allow_html=True)

col_right, col_mid, col_left = st.columns([1.1, 1.8, 1.1])

with col_right:
    st.subheader("📏 2- الأبعاد")
    dim = st.selectbox("المقاس:", ["Shorts (9:16)", "YouTube (16:9)", "Square (1:1)"])
    st.divider()

    st.subheader("🎙️ 3- هندسة الصوت")
    v_src = st.radio("المصدر:", ["بشري 🎤", "AI 🤖", "ElevenLabs 💎"], index=0)
    if v_src == "بشري 🎤":
        u_voice = st.file_uploader("📥 أيقونة تحميل الصوت البشري:")
        voice_text = st.text_area("✍️ نص اختياري:")
    elif v_src == "ElevenLabs 💎":
        el_k = st.text_input("🔑 API Key")
        el_m = st.text_input("📦 Model ID")
        voice_text = st.text_area("✍️ نص ElevenLabs:")
    else:
        voice_text = st.text_area("✍️ نص الـ AI:")
    st.divider()
    st.subheader("🎭 1- النمط")
    m_style = st.selectbox("الروح:", ["سينمائي 🎬", "درامي 🎭", "وثائقي 📜"])

with col_left:
    st.subheader("🖼️ 4- محرك الصور")
    img_mode = st.radio("الجلب:", ["يدوي (رفع) 📁", "أوتوماتيك ✨"])
    if img_mode == "يدوي (رفع) 📁":
        u_imgs = st.file_uploader("📁 ارفع صورك:", accept_multiple_files=True)
    else:
        img_q = st.text_input("🔍 كلمات مفتاحية:")
    
    st.divider()
    st.subheader("🎨 8, 9- الهوية (مهم)")
    use_logo = st.toggle("9- إضافة لوجو (سيظهر دائماً)", value=True)
    u_logo = st.file_uploader("🖼️ تحميل صورة اللوجو (PNG شفافة يفضل):") if use_logo else None
    
    use_banner = st.toggle("8- بنر سفلي")
    banner_txt = st.text_input("✍️ نص البنر:") if use_banner else ""

with col_mid:
    st.markdown("<div class='render-zone'>", unsafe_allow_html=True)
    st.subheader("📺 شاشة الإنتاج المركزي")
    
    if st.button("🚀 إطلاق رندر الإنجاز (V124)"):
        if v_src == "بشري 🎤" and not u_voice:
            st.error("ارفع ملف الصوت أولاً!")
        else:
            try:
                with st.spinner("⏳ جاري تثبيت اللوجو والمونتاج..."):
                    # 1. الصوت
                    v_p = os.path.join(ASSETS_DIR, "v.mp3")
                    if v_src == "بشري 🎤":
                        with open(v_p, "wb") as f: f.write(u_voice.getbuffer())
                    else:
                        gTTS(voice_text, lang='ar').save(v_p)
                    audio = AudioFileClip(v_p)

                    # 2. الأبعاد والمشاهد
                    w, h = (1080, 1920) if "9:16" in dim else (1920, 1080)
                    num_scenes = len(u_imgs) if img_mode == "يدوي (رفع) 📁" and u_imgs else 5
                    dur = audio.duration / num_scenes
                    
                    clips = []
                    for i in range(num_scenes):
                        img_p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
                        if img_mode == "يدوي (رفع) 📁":
                            with open(img_p, "wb") as f: f.write(u_imgs[i % len(u_imgs)].getbuffer())
                        else:
                            resp = requests.get(f"https://picsum.photos/seed/{i}/{w}/{h}")
                            Image.open(io.BytesIO(resp.content)).save(img_p)
                        
                        c = ImageClip(img_p)
                        c = c.set_duration(dur + 0.4) if hasattr(c, 'set_duration') else c.with_duration(dur + 0.4)
                        
                        # الزووم
                        z = 1.1 if i % 2 == 0 else 0.9
                        c = c.resize(lambda t: 1 + (z-1) * (t / dur)) if hasattr(c, 'resize') else c.resized(lambda t: 1 + (z-1) * (t / dur))
                        clips.append(c.crossfadein(0.4))

                    main_video = concatenate_videoclips(clips, method="compose", padding=-0.3)

                    # 3. الهوية (اللوجو - إصلاح الظهور)
                    layers = [main_video]
                    if use_logo and u_logo:
                        lp = os.path.join(ASSETS_DIR, "logo_final.png")
                        # معالجة اللوجو لضمان الشفافية والحجم
                        img_logo = Image.open(u_logo).convert("RGBA")
                        img_logo.thumbnail((w//6, w//6)) # تصغير اللوجو ليكون مناسباً
                        img_logo.save(lp)
                        
                        l_c = ImageClip(lp).set_start(0) # يبدأ من الثانية صفر
                        # تثبيت المدة لتساوي مدة الصوت بالملي
                        l_c = l_c.set_duration(audio.duration) if hasattr(l_c, 'set_duration') else l_c.with_duration(audio.duration)
                        # وضعه في أعلى اليمين مع "هامش" بسيط 20 بكسل
                        l_c = l_c.set_position(("right", 20)) if hasattr(l_c, 'set_position') else l_c.with_position(("right", 20))
                        layers.append(l_c) # إضافته كطبقة علوية

                    final = CompositeVideoClip(layers, size=(w, h))
                    final = final.set_audio(audio) if hasattr(final, 'set_audio') else final.with_audio(audio)
                    
                    out_f = os.path.join(VIDEOS_DIR, "Output_V124.mp4")
                    final.write_videofile(out_f, fps=24, codec="libx264")
                    
                    st.video(out_f)
                    st.success("🎯 مبروك! اللوجو دلوقتِ ثابت ومنور الفيديو.")

            except Exception as e: st.error(f"خطأ فني: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
