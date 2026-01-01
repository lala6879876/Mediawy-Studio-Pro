import streamlit as st
import os, requests, io, random
from PIL import Image
from gtts import gTTS

try:
    from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
except ImportError:
    from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips

# --- 1. التأسيس ---
MEDIA_DIR = "Mediawy_Studio_V128"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- واجهة Dashboard (عصرية - بيضاء - فونت صغير) ---
st.set_page_config(page_title="Mediawy V128 Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333; font-size: 13px; }
    .render-zone { border: 2px solid #007BFF; padding: 20px; border-radius: 15px; background-color: #fcfcfc; }
    h2, h3 { color: #007BFF !important; font-size: 0.9rem !important; font-weight: bold; }
    .stDivider { margin: 8px 0 !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#007BFF; font-size:24px;'>🎬 Mediawy Studio V128 - Rhythm Master</h1>", unsafe_allow_html=True)

col_right, col_mid, col_left = st.columns([1.1, 1.8, 1.1])

with col_right:
    st.subheader("📏 2- الأبعاد")
    dim = st.selectbox("المقاس:", ["Shorts (9:16)", "YouTube (16:9)", "Square (1:1)"])
    st.divider()

    st.subheader("🎙️ 3- هندسة الصوت")
    v_src = st.radio("المصدر:", ["بشري 🎤", "AI 🤖", "ElevenLabs 💎"], index=0)
    if v_src == "بشري 🎤":
        u_voice = st.file_uploader("📥 تحميل الصوت البشري:")
        voice_text = st.text_area("✍️ نص اختياري:")
    elif v_src == "ElevenLabs 💎":
        el_col1, el_col2 = st.columns(2)
        with el_col1: el_key = st.text_input("🔑 API Key")
        with el_col2: el_mod = st.text_input("📦 Model ID")
        voice_text = st.text_area("✍️ نص ElevenLabs:")
    else:
        voice_text = st.text_area("✍️ نص الـ AI:")
    st.divider()
    st.subheader("🎭 1- النمط")
    m_style = st.selectbox("الروح:", ["إيقاعي متزن ⚖️", "سينمائي 🎬", "هادئ ☁️"])

with col_left:
    st.subheader("🖼️ 4- محرك الصور")
    img_mode = st.radio("الجلب:", ["يدوي 📁", "أوتوماتيك ✨"])
    if img_mode == "يدوي 📁":
        u_imgs = st.file_uploader("📁 ارفع صورك (حتى 500):", accept_multiple_files=True)
    else:
        img_q = st.text_input("🔍 كلمات البحث:")
    
    st.divider()
    st.subheader("🎨 8, 9- الهوية")
    use_logo = st.toggle("9- إضافة لوجو", value=True)
    u_logo = st.file_uploader("🖼️ تحميل اللوجو (PNG):") if use_logo else None
    use_banner = st.toggle("8- بنر سفلي")
    banner_txt = st.text_input("✍️ نص البنر:") if use_banner else ""

with col_mid:
    st.markdown("<div class='render-zone'>", unsafe_allow_html=True)
    st.subheader("📺 شاشة الإنتاج المركزي")
    
    # تحكم متقدم في الإيقاع
    fade_val = st.slider("⏱️ قوة التلاشي (النقلة الناعمة):", 0.3, 1.0, 0.5)
    zoom_val = st.slider("🔍 قوة الزووم الخفيف (للصور المختارة):", 1.02, 1.10, 1.05)

    if st.button("🚀 إطلاق رندر الإيقاع المتزن"):
        if (v_src == "بشري 🎤" and not u_voice) or (img_mode == "يدوي 📁" and not u_imgs):
            st.error("تأكد من رفع ملف الصوت والصور أولاً!")
        else:
            try:
                with st.spinner("⏳ جاري تنسيق الإيقاع البصري..."):
                    # 1. الصوت
                    v_p = os.path.join(ASSETS_DIR, "v.mp3")
                    if v_src == "بشري 🎤":
                        with open(v_p, "wb") as f: f.write(u_voice.getbuffer())
                    else:
                        gTTS(voice_text, lang='ar').save(v_p)
                    audio = AudioFileClip(v_p)

                    # 2. الأبعاد والمشاهد
                    w, h = (1080, 1920) if "9:16" in dim else (1920, 1080)
                    num_scenes = len(u_imgs) if img_mode == "يدوي 📁" else 6
                    dur = audio.duration / num_scenes
                    
                    clips = []
                    for i in range(num_scenes):
                        img_p = os.path.join(ASSETS_DIR, f[f"i_{i}.jpg"])
                        if img_mode == "يدوي 📁":
                            with open(img_p, "wb") as f: f.write(u_imgs[i % len(u_imgs)].getbuffer())
                        else:
                            resp = requests.get(f"https://picsum.photos/seed/{i}/{w}/{h}")
                            Image.open(io.BytesIO(resp.content)).save(img_p)
                        
                        c = ImageClip(img_p)
                        c = c.set_duration(dur + fade_val) if hasattr(c, 'set_duration') else c.with_duration(dur + fade_val)
                        
                        # --- منطق "صورة آه وصورة لأ" ---
                        if i % 2 == 0:
                            # زووم خفيف جداً وهادئ
                            c = c.resize(lambda t: 1 + (zoom_val-1) * (t / dur)) if hasattr(c, 'resize') else c.resized(lambda t: 1 + (zoom_val-1) * (t / dur))
                        else:
                            # صورة ثابتة تماماً
                            pass
                        
                        # النقلة الناعمة
                        c = c.crossfadein(fade_val).crossfadeout(fade_val)
                        clips.append(c)

                    main_video = concatenate_videoclips(clips, method="compose", padding=-fade_val)

                    # 3. الطبقات (اللوجو والبنر)
                    layers = [main_video]
                    if use_logo and u_logo:
                        lp = os.path.join(ASSETS_DIR, "logo.png")
                        Image.open(u_logo).convert("RGBA").resize((w//7, w//7)).save(lp)
                        l_c = ImageClip(lp).set_start(0)
                        l_c = l_c.set_duration(audio.duration) if hasattr(l_c, 'set_duration') else l_c.with_duration(audio.duration)
                        l_c = l_c.set_position(("right", 30)) if hasattr(l_c, 'set_position') else l_c.with_position(("right", 30))
                        layers.append(l_c)

                    final = CompositeVideoClip(layers, size=(w, h))
                    final = final.set_audio(audio) if hasattr(final, 'set_audio') else final.with_audio(audio)
                    
                    out_f = os.path.join(VIDEOS_DIR, "Mediawy_Rhythm_V128.mp4")
                    final.write_videofile(out_f, fps=24, codec="libx264")
                    
                    st.video(out_f)
                    st.success("🎯 فيديو احترافي بإيقاع متوازن جاهز للعرض!")

            except Exception as e: st.error(f"خطأ فني: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
