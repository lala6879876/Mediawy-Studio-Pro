import streamlit as st
import os, requests, re, io, random
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS

# --- معالجة التوافق بين إصدارات MoviePy المختلفة ---
try:
    from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, vfx
except ImportError:
    from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, vfx

# --- 1. إعداد البيئة ---
MEDIA_DIR = "Mediawy_Studio_V119"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- واجهة المستخدم (التصميم الأبيض الأنيق) ---
st.set_page_config(page_title="Mediawy V119 Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333; }
    .render-box { border: 2px solid #007BFF; padding: 20px; border-radius: 15px; background: #FAFAFA; }
    h2, h3 { color: #007BFF !important; font-size: 1rem !important; margin-bottom: 5px; }
    .stDivider { margin: 12px 0 !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#007BFF; font-size:28px;'>🎬 Mediawy Studio V119</h1>", unsafe_allow_html=True)

# توزيع Dashboard: يمين (تحكم) - منتصف (إنتاج) - يسار (هوية)
col_right, col_mid, col_left = st.columns([1.1, 1.8, 1.1])

# --- الجانب الأيمن (هندسة الصوت والأبعاد) ---
with col_right:
    st.subheader("📏 2- الأبعاد")
    dim = st.selectbox("المقاس:", ["Shorts (9:16)", "YouTube (16:9)", "Instagram (4:5)", "Square (1:1)"])
    st.divider()

    st.subheader("🎙️ 3- هندسة الصوت")
    v_src = st.radio("المصدر:", ["بشري 🎤", "AI 🤖", "ElevenLabs 💎"], index=0)
    
    if v_src == "بشري 🎤":
        u_voice = st.file_uploader("📥 أيقونة تحميل الصوت البشري:")
        voice_text = st.text_area("✍️ نص اختياري (للترجمة فقط):")
    elif v_src == "AI 🤖":
        voice_text = st.text_area("✍️ اكتب النص هنا:")
    elif v_src == "ElevenLabs 💎":
        # الـ 3 مربعات المطلوبة
        el_key = st.text_input("🔑 API Key")
        el_mod = st.text_input("📦 Model ID")
        voice_text = st.text_area("✍️ نص ElevenLabs")
    st.divider()
    
    st.subheader("🎭 1- النمط")
    m_style = st.selectbox("الروح العامة:", ["سينمائي 🎬", "درامي 🎭", "وثائقي 📜"])

# --- الجانب الأيسر (الصور والهوية) ---
with col_left:
    st.subheader("🖼️ 4- محرك الصور")
    img_mode = st.radio("الجلب:", ["أوتوماتيك ✨", "يدوي 📁"])
    if img_mode == "يدوي 📁":
        u_imgs = st.file_uploader("📁 ارفع صورك (حتى 500 صورة):", accept_multiple_files=True)
    else:
        img_q = st.text_input("🔍 مربع الكلمات المفتاحية للصور:")
    st.divider()

    st.subheader("🎨 8, 9- الهوية")
    use_logo = st.toggle("9- إضافة لوجو (أعلى يمين)")
    u_logo = st.file_uploader("🖼️ تحميل اللوجو:") if use_logo else None
    
    use_banner = st.toggle("8- بنر سفلي")
    banner_txt = st.text_input("✍️ نص البنر والتعليق:") if use_banner else ""

# --- العمود الأوسط (شاشة الإنتاج والـ SEO) ---
with col_mid:
    st.markdown("<div class='render-box'>", unsafe_allow_html=True)
    st.subheader("📺 شاشة الإنتاج المركزي")
    
    

    if st.button("🚀 إطلاق رندر الإنجاز الملياري"):
        if v_src == "بشري 🎤" and not u_voice:
            st.error("ارفع ملف الصوت البشري أولاً!")
        else:
            try:
                with st.spinner("⏳ جاري المونتاج وتوافق الطبقات..."):
                    # 1. الصوت
                    v_p = os.path.join(ASSETS_DIR, "v.mp3")
                    if v_src == "بشري 🎤":
                        with open(v_p, "wb") as f: f.write(u_voice.getbuffer())
                    else:
                        gTTS(voice_text, lang='ar').save(v_p)
                    audio = AudioFileClip(v_p)

                    # 2. الأبعاد
                    w, h = (1080, 1920) if "9:16" in dim else (1920, 1080)
                    
                    # 3. بناء المشاهد (توافق الإصدارات)
                    num_scenes = 5
                    dur = audio.duration / num_scenes
                    clips = []

                    for i in range(num_scenes):
                        img_p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
                        if img_mode == "أوتوماتيك ✨":
                            resp = requests.get(f"https://picsum.photos/seed/{random.randint(1,999)}/{w}/{h}")
                            Image.open(io.BytesIO(resp.content)).save(img_p)
                        else:
                            with open(img_p, "wb") as f: f.write(u_imgs[i % len(u_imgs)].getbuffer())
                        
                        # --- التعامل الذكي مع أسماء الدوال ---
                        c = ImageClip(img_p)
                        if hasattr(c, 'with_duration'): c = c.with_duration(dur + 0.4)
                        else: c = c.set_duration(dur + 0.4)
                        
                        # زووم ان وزووم اوت (5)
                        z = 1.12 if i % 2 == 0 else 0.88
                        def resize_func(t): return 1 + (z-1) * (t / dur)
                        
                        if hasattr(c, 'resized'): c = c.resized(resize_func)
                        else: c = c.resize(resize_func)
                        
                        clips.append(c.crossfadein(0.4))

                    video = concatenate_videoclips(clips, method="compose", padding=-0.3)

                    # 4. الهوية (اللوجو والبنر)
                    layers = [video]
                    if use_logo and u_logo:
                        lp = os.path.join(ASSETS_DIR, "l.png")
                        Image.open(u_logo).convert("RGBA").resize((w//8, w//8)).save(lp)
                        l_clip = ImageClip(lp)
                        if hasattr(l_clip, 'with_duration'): l_clip = l_clip.with_duration(audio.duration)
                        else: l_clip = l_clip.set_duration(audio.duration)
                        layers.append(l_clip.set_position(("right", 20)))

                    final = CompositeVideoClip(layers, size=(w, h))
                    if hasattr(final, 'with_audio'): final = final.with_audio(audio)
                    else: final = final.set_audio(audio)
                    
                    out_f = os.path.join(VIDEOS_DIR, "Mediawy_Success_V119.mp4")
                    final.write_videofile(out_f, fps=24, codec="libx264")
                    
                    st.video(out_f)
                    st.success("🎯 تم الرندر بنجاح!")

                    # 10. الـ SEO
                    st.divider()
                    st.markdown("### 📊 10- ملخص الـ SEO والبيانات")
                    st.info(f"**الاسم المقترح:** {img_q if img_q else 'فيديو احترافي'}\n\n**الكلمات:** {img_q}\n\n**الهاشتاج:** #AI #Production #Mediawy")
            
            except Exception as e:
                st.error(f"حدث خطأ فني: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
