import streamlit as st
import os, requests, re, io, random
from PIL import Image
from gtts import gTTS

# استيراد محرك المونتاج
try:
    from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, vfx
except ImportError:
    from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, vfx

# --- 1. تأسيس الاستوديو ---
MEDIA_DIR = "Mediawy_Studio_V121"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- واجهة Dashboard بيضاء احترافية ---
st.set_page_config(page_title="Mediawy V121 Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333; }
    .render-zone { border: 2px solid #007BFF; padding: 25px; border-radius: 15px; background-color: #FAFAFA; }
    h2, h3 { color: #007BFF !important; font-size: 1rem !important; }
    .stDivider { margin: 15px 0 !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#007BFF;'>🎬 Mediawy Studio V121 - Professional</h1>", unsafe_allow_html=True)

# التوزيع الثلاثي (تحكم - إنتاج - هوية)
col_right, col_mid, col_left = st.columns([1.1, 1.8, 1.1])

with col_right:
    st.subheader("📏 2- الأبعاد")
    dim = st.selectbox("المقاس:", ["Shorts (9:16)", "YouTube (16:9)", "Square (1:1)"])
    st.divider()

    st.subheader("🎙️ 3- هندسة الصوت")
    v_src = st.radio("المصدر:", ["بشري 🎤", "AI 🤖", "ElevenLabs 💎"], index=0)
    if v_src == "بشري 🎤":
        u_voice = st.file_uploader("📥 ارفع الصوت المسجل:")
        voice_text = st.text_area("✍️ نص اختياري (للملخص):")
    elif v_src == "ElevenLabs 💎":
        el_key = st.text_input("🔑 API Key")
        el_mod = st.text_input("📦 Model ID")
        voice_text = st.text_area("✍️ نص ElevenLabs")
    else:
        voice_text = st.text_area("✍️ اكتب نص الـ AI:")

with col_left:
    st.subheader("🖼️ 4- محرك الصور")
    img_mode = st.radio("الجلب:", ["يدوي 📁", "أوتوماتيك ✨"])
    if img_mode == "يدوي 📁":
        u_imgs = st.file_uploader("📁 ارفع صورك (حتى 500):", accept_multiple_files=True)
    else:
        img_q = st.text_input("🔍 كلمات مفتاحية:")
    st.divider()

    st.subheader("🎨 8, 9- الهوية")
    use_logo = st.toggle("9- إضافة لوجو")
    u_logo = st.file_uploader("تحميل اللوجو:") if use_logo else None
    use_banner = st.toggle("8- بنر سفلي")
    banner_txt = st.text_input("نص البنر:") if use_banner else ""

with col_mid:
    st.markdown("<div class='render-zone'>", unsafe_allow_html=True)
    st.subheader("📺 شاشة الإنتاج المركزي")
    
    if st.button("🚀 إطلاق رندر الإنجاز النهائي"):
        if v_src == "بشري 🎤" and not u_voice:
            st.error("ارفع ملف الصوت أولاً!")
        else:
            try:
                with st.spinner("⏳ جاري المونتاج بالتقنيات الحديثة..."):
                    # 1. الصوت
                    v_p = os.path.join(ASSETS_DIR, "v.mp3")
                    if v_src == "بشري 🎤":
                        with open(v_p, "wb") as f: f.write(u_voice.getbuffer())
                    else:
                        gTTS(voice_text, lang='ar').save(v_p)
                    audio = AudioFileClip(v_p)

                    # 2. الأبعاد والمشاهد
                    w, h = (1080, 1920) if "9:16" in dim else (1920, 1080)
                    num_scenes = len(u_imgs) if img_mode == "يدوي 📁" and u_imgs else 5
                    dur = audio.duration / num_scenes
                    
                    clips = []
                    for i in range(num_scenes):
                        img_p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
                        if img_mode == "يدوي 📁":
                            with open(img_p, "wb") as f: f.write(u_imgs[i % len(u_imgs)].getbuffer())
                        else:
                            resp = requests.get(f"https://picsum.photos/seed/{random.randint(1,999)}/{w}/{h}")
                            Image.open(io.BytesIO(resp.content)).save(img_p)
                        
                        # --- الحل الجذري: استخدام with_ بدل set_ ---
                        c = ImageClip(img_p)
                        
                        # التوافق مع MoviePy 2.0+
                        if hasattr(c, 'with_duration'):
                            c = c.with_duration(dur + 0.4)
                        else:
                            c = c.set_duration(dur + 0.4)
                            
                        # الزووم
                        z = 1.1 if i % 2 == 0 else 0.9
                        if hasattr(c, 'resized'):
                            c = c.resized(lambda t: 1 + (z-1) * (t / dur))
                        else:
                            c = c.resize(lambda t: 1 + (z-1) * (t / dur))
                            
                        clips.append(c.with_effects([vfx.CrossFadeIn(0.4)]) if hasattr(c, 'with_effects') else c.crossfadein(0.4))

                    video = concatenate_videoclips(clips, method="compose", padding=-0.3)

                    # 3. الهوية
                    layers = [video]
                    if use_logo and u_logo:
                        lp = os.path.join(ASSETS_DIR, "l.png")
                        Image.open(u_logo).convert("RGBA").resize((w//8, w//8)).save(lp)
                        l_clip = ImageClip(lp)
                        l_clip = l_clip.with_duration(audio.duration) if hasattr(l_clip, 'with_duration') else l_clip.set_duration(audio.duration)
                        layers.append(l_clip.with_position(("right", 20)) if hasattr(l_clip, 'with_position') else l_clip.set_position(("right", 20)))

                    final = CompositeVideoClip(layers, size=(w, h))
                    final = final.with_audio(audio) if hasattr(final, 'with_audio') else final.set_audio(audio)
                    
                    out_f = os.path.join(VIDEOS_DIR, "Mediawy_V121_Final.mp4")
                    final.write_videofile(out_f, fps=24, codec="libx264")
                    
                    st.video(out_f)
                    st.success("🎯 مبروك! تم الرندر بنجاح باهر.")

                    # 10. SEO
                    st.divider()
                    st.markdown("### 📊 ملخص الـ SEO")
                    st.info(f"**الاسم:** {img_q if img_mode == 'أوتوماتيك ✨' else 'Manual Edit'}\n\n**الهاشتاجات:** #AI #Manual_Edit #Mediawy")
            
            except Exception as e:
                st.error(f"خطأ: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
