import streamlit as st
import os, requests, re, io, random
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS

# --- معالجة الاستيراد لضمان العمل على أي منصة ---
try:
    from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, vfx
except ImportError:
    try:
        from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, vfx
    except:
        st.error("برجاء تثبيت مكتبة moviepy عن طريق: pip install moviepy")

# --- 1. إعداد البيئة الفنية ---
MEDIA_DIR = "Mediawy_V120_Manual_Pro"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- دالة "المصلي" لضمان عمل الدوال (Duration / Audio / Position) ---
def safe_set(clip, attr_name, value):
    # تحويل الأسماء القديمة للجديدة أوتوماتيكياً حسب نسخة المكتبة
    map_dict = {
        "set_duration": "with_duration",
        "set_audio": "with_audio",
        "set_position": "with_position",
        "resize": "resized"
    }
    alt_name = map_dict.get(attr_name, attr_name)
    if hasattr(clip, attr_name):
        return getattr(clip, attr_name)(value)
    elif hasattr(clip, alt_name):
        return getattr(clip, alt_name)(value)
    return clip

# --- واجهة المستخدم (الخلفية البيضاء والتنسيق الهندسي) ---
st.set_page_config(page_title="Mediawy V120", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #333; }
    .render-box { border: 2px solid #007BFF; padding: 20px; border-radius: 15px; background: #FAFAFA; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    h2, h3 { color: #007BFF !important; font-size: 1rem !important; }
    .stDivider { margin: 15px 0 !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#007BFF;'>🎬 Mediawy Studio V120 - Manual Master</h1>", unsafe_allow_html=True)

# التوزيع: يمين (تحكم) - منتصف (إنتاج) - يسار (إضافات)
col_right, col_mid, col_left = st.columns([1.1, 1.8, 1.1])

with col_right:
    st.subheader("📏 2- الأبعاد")
    dim = st.selectbox("المقاس:", ["Shorts (9:16)", "YouTube (16:9)", "Square (1:1)"])
    st.divider()

    st.subheader("🎙️ 3- هندسة الصوت")
    v_src = st.radio("المصدر:", ["بشري 🎤", "AI 🤖", "ElevenLabs 💎"], index=0)
    if v_src == "بشري 🎤":
        u_voice = st.file_uploader("📥 ارفع صوتك المسجل:")
        voice_text = st.text_area("✍️ نص اختياري (للملخص):")
    elif v_src == "ElevenLabs 💎":
        el_key = st.text_input("🔑 API Key")
        el_mod = st.text_input("📦 Model ID")
        voice_text = st.text_area("✍️ نص ElevenLabs")
    else:
        voice_text = st.text_area("✍️ اكتب نص الـ AI:")

with col_left:
    st.subheader("🖼️ 4- محرك الصور (يدوي)")
    img_mode = st.radio("الجلب:", ["يدوي (رفع صور) 📁", "أوتوماتيك ✨"])
    if img_mode == "يدوي (رفع صور) 📁":
        u_imgs = st.file_uploader("📁 ارفع صورك (حتى 500 صورة):", accept_multiple_files=True)
    else:
        img_q = st.text_input("🔍 كلمات مفتاحية:")
    st.divider()

    st.subheader("🎨 8, 9- الهوية")
    use_logo = st.toggle("إضافة لوجو")
    u_logo = st.file_uploader("تحميل اللوجو:") if use_logo else None
    use_banner = st.toggle("تفعيل البنر")
    banner_txt = st.text_input("نص البنر:") if use_banner else ""

with col_mid:
    st.markdown("<div class='render-box'>", unsafe_allow_html=True)
    st.subheader("📺 شاشة الإنتاج المركزي")
    
    

    if st.button("🚀 إطلاق الرندر اليدوي المضمون"):
        if v_src == "بشري 🎤" and not u_voice:
            st.error("ارفع ملف الصوت أولاً!")
        elif img_mode == "يدوي (رفع صور) 📁" and not u_imgs:
            st.error("ارفع الصور يدوياً أولاً!")
        else:
            try:
                with st.spinner("⏳ جاري المونتاج وتوافق النسخ..."):
                    # 1. الصوت
                    v_p = os.path.join(ASSETS_DIR, "v.mp3")
                    if v_src == "بشري 🎤":
                        with open(v_p, "wb") as f: f.write(u_voice.getbuffer())
                    else:
                        gTTS(voice_text, lang='ar').save(v_p)
                    audio = AudioFileClip(v_p)

                    # 2. الأبعاد والمشاهد
                    w, h = (1080, 1920) if "9:16" in dim else (1920, 1080)
                    num_scenes = len(u_imgs) if img_mode == "يدوي (رفع صور) 📁" else 5
                    dur = audio.duration / num_scenes
                    
                    clips = []
                    for i in range(num_scenes):
                        img_p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
                        if img_mode == "يدوي (رفع صور) 📁":
                            with open(img_p, "wb") as f: f.write(u_imgs[i].getbuffer())
                        else:
                            resp = requests.get(f"https://picsum.photos/seed/{i}/{w}/{h}")
                            Image.open(io.BytesIO(resp.content)).save(img_p)
                        
                        # تطبيق الدوال "بأمان" لتجنب الخطأ
                        c = ImageClip(img_p)
                        c = safe_set(c, "set_duration", dur + 0.5)
                        
                        # زووم ان وزووم اوت
                        z = 1.12 if i % 2 == 0 else 0.88
                        c = safe_set(c, "resize", lambda t: 1 + (z-1) * (t / dur))
                        clips.append(c.crossfadein(0.4))

                    video = concatenate_videoclips(clips, method="compose", padding=-0.3)

                    # 3. الهوية (اللوجو)
                    layers = [video]
                    if use_logo and u_logo:
                        lp = os.path.join(ASSETS_DIR, "l.png")
                        Image.open(u_logo).convert("RGBA").resize((w//8, w//8)).save(lp)
                        l_clip = ImageClip(lp)
                        l_clip = safe_set(l_clip, "set_duration", audio.duration)
                        l_clip = safe_set(l_clip, "set_position", ("right", 20))
                        layers.append(l_clip)

                    final = CompositeVideoClip(layers, size=(w, h))
                    final = safe_set(final, "set_audio", audio)
                    
                    out_f = os.path.join(VIDEOS_DIR, "Mediawy_Manual_Success.mp4")
                    final.write_videofile(out_f, fps=24, codec="libx264")
                    
                    st.video(out_f)
                    st.success("🎯 تم الرندر اليدوي بنجاح!")

                    # 10. الـ SEO
                    st.divider()
                    st.markdown("### 📊 ملخص الـ SEO")
                    st.info(f"**الاسم:** {voice_text[:30] if voice_text else 'Manual Edit'}\n\n**الهاشتاج:** #Manual_Production #AI")
            
            except Exception as e:
                st.error(f"حدث خطأ فني: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
