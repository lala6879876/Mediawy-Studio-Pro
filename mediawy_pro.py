import streamlit as st
import os, requests, re, io, random
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS

# محرك المونتاج (التوافق الشامل)
try:
    from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, vfx
except ImportError:
    from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, vfx

# --- 1. إعداد الاستوديو ---
MEDIA_DIR = "Mediawy_Studio_V122"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- واجهة Dashboard (عصرية - أنيقة - بيضاء) ---
st.set_page_config(page_title="Mediawy V122 Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #2D3436; font-family: 'Arial'; }
    .side-panel { background-color: #F9F9F9; padding: 20px; border-radius: 10px; border: 1px solid #EEE; }
    .render-zone { border: 2px solid #007BFF; padding: 25px; border-radius: 20px; background-color: #FAFAFA; }
    h2, h3 { color: #007BFF !important; font-size: 1rem !important; margin-bottom: 10px; }
    .stDivider { margin: 15px 0 !important; }
    .stButton>button { background: #007BFF; color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 50px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#007BFF;'>🎬 Mediawy Studio V122 - Professional Edition</h1>", unsafe_allow_html=True)

# --- تقسيم الاستوديو (3 أعمدة) ---
col_right, col_mid, col_left = st.columns([1.1, 1.8, 1.1])

# --- الجانب الأيمن: التحكم الصوتي والأبعاد ---
with col_right:
    st.subheader("📏 2- الأبعاد والمنصة")
    dim = st.selectbox("المقاس:", ["Shorts/TikTok (9:16)", "YouTube Standard (16:9)", "Square (1:1)"])
    st.divider() # 11- فواصل

    st.subheader("🎙️ 3- هندسة الصوت")
    v_src = st.radio("المصدر:", ["بشري 🎤", "AI 🤖", "ElevenLabs 💎"], index=0)
    
    if v_src == "بشري 🎤":
        u_voice = st.file_uploader("📥 أيقونة تحميل الصوت البشري:")
        voice_text = st.text_area("✍️ النص (اختياري للترجمة والـ SEO):")
    elif v_src == "ElevenLabs 💎":
        el_key = st.text_input("🔑 API Key")
        el_mod = st.text_input("📦 Model ID")
        voice_text = st.text_area("✍️ نص ElevenLabs:")
    else:
        voice_text = st.text_area("✍️ مربع كتابة نص الـ AI:")
    st.divider()
    
    st.subheader("🎭 1- نمط المونتاج")
    m_style = st.selectbox("الروح العامة:", ["سينمائي 🎬", "درامي 🎭", "وثائقي 📜"])

# --- الجانب الأيسر: الصور والهوية ---
with col_left:
    st.subheader("🖼️ 4- محرك الصور")
    img_mode = st.radio("الجلب:", ["يدوي (رفع) 📁", "اتوماتيك ✨"])
    if img_mode == "يدوي (رفع) 📁":
        u_imgs = st.file_uploader("📁 أيقونة الرفع (حتى 500 صورة):", accept_multiple_files=True)
    else:
        img_q = st.text_input("🔍 مربع الكلمات المفتاحية:")
    st.divider()

    st.subheader("🎨 8, 9- الهوية والبصمة")
    use_logo = st.toggle("9- إضافة لوجو (أعلى يمين)")
    u_logo = st.file_uploader("🖼️ تحميل اللوجو:") if use_logo else None
    
    use_banner = st.toggle("8- بنر سفلي احترافي")
    banner_txt = st.text_input("✍️ مربع نص البنر:") if use_banner else ""

# --- العمود الأوسط: شاشة الإنتاج والـ SEO ---
with col_mid:
    st.markdown("<div class='render-zone'>", unsafe_allow_html=True)
    st.subheader("📺 شاشة الإنتاج المركزي")
    
    show_subs = st.toggle("7- ترجمة كلمة بكلمة (اختياري)", value=True)

    if st.button("🚀 إطلاق الرندر الملياري (V122)"):
        if v_src == "بشري 🎤" and not u_voice:
            st.error("ارفع ملف الصوت البشري أولاً!")
        else:
            try:
                with st.spinner("⏳ جاري المونتاج وتوافق الأنظمة..."):
                    # 1. الصوت
                    v_p = os.path.join(ASSETS_DIR, "v.mp3")
                    if v_src == "بشري 🎤":
                        with open(v_p, "wb") as f: f.write(u_voice.getbuffer())
                    else:
                        gTTS(voice_text, lang='ar').save(v_p)
                    audio = AudioFileClip(v_p)

                    # 2. الأبعاد
                    w, h = (1080, 1920) if "9:16" in dim else (1920, 1080)
                    
                    # 3. بناء المشاهد (توافق شامل مع MoviePy)
                    num_scenes = len(u_imgs) if img_mode == "يدوي (رفع) 📁" and u_imgs else 5
                    dur = audio.duration / num_scenes
                    clips = []

                    

                    for i in range(num_scenes):
                        img_p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
                        if img_mode == "يدوي (رفع) 📁":
                            with open(img_p, "wb") as f: f.write(u_imgs[i % len(u_imgs)].getbuffer())
                        else:
                            resp = requests.get(f"https://picsum.photos/seed/{random.randint(1,999)}/{w}/{h}")
                            Image.open(io.BytesIO(resp.content)).save(img_p)
                        
                        # الإنتاج المضمون (الحل الجذري للدوال)
                        c = ImageClip(img_p)
                        # فحص ذكي للدوال (set_duration vs with_duration)
                        c = c.set_duration(dur + 0.4) if hasattr(c, 'set_duration') else c.with_duration(dur + 0.4)
                        
                        # الزووم
                        z = 1.15 if i % 2 == 0 else 0.85
                        def resize_f(t): return 1 + (z-1) * (t / dur)
                        c = c.resize(resize_f) if hasattr(c, 'resize') else c.resized(resize_f)
                        
                        clips.append(c.crossfadein(0.4))

                    video = concatenate_videoclips(clips, method="compose", padding=-0.3)

                    # 4. الهوية واللوجو
                    layers = [video]
                    if use_logo and u_logo:
                        lp = os.path.join(ASSETS_DIR, "l.png")
                        Image.open(u_logo).convert("RGBA").resize((w//8, w//8)).save(lp)
                        l_c = ImageClip(lp)
                        l_c = l_c.set_duration(audio.duration) if hasattr(l_c, 'set_duration') else l_c.with_duration(audio.duration)
                        layers.append(l_c.set_position(("right", 20)) if hasattr(l_c, 'set_position') else l_c.with_position(("right", 20)))

                    final = CompositeVideoClip(layers, size=(w, h))
                    final = final.set_audio(audio) if hasattr(final, 'set_audio') else final.with_audio(audio)
                    
                    out_f = os.path.join(VIDEOS_DIR, "Mediawy_Final_V122.mp4")
                    final.write_videofile(out_f, fps=24, codec="libx264")
                    
                    st.video(out_f)
                    st.success("🎯 مبروك! تم الرندر بنجاح باهر.")

                    # 10. ملخص الـ SEO اسفل الفيديو
                    st.divider()
                    st.markdown("### 📊 10- ملخص الـ SEO والبيانات")
                    st.info(f"**الاسم المقترح:** {voice_text[:40] if voice_text else 'فيديو احترافي'}\n\n**الكلمات:** {img_q if img_mode == 'اتوماتيك ✨' else 'تنسيق يدوي'}\n\n**الهاشتاجات:** #AI #Production #Mediawy")

            except Exception as e:
                st.error(f"حدث خطأ فني: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
