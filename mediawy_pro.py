import streamlit as st
import os, requests, re, io, time, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip, vfx

# --- 1. إعداد البيئة الفنية ---
MEDIA_DIR = "Mediawy_Ultra_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- محرك الصور الذكي ---
def get_cinematic_image(query, path, size, style):
    w, h = size
    q = "+".join(re.findall(r'\w+', query)[:3])
    # إضافة لمسة النمط للبحث
    style_query = "documentary,historical" if style == "وثائقي 🎞️" else "cinematic,dramatic"
    url = f"https://source.unsplash.com/featured/{w}x{h}/?{q},{style_query}&sig={random.randint(1,1000)}"
    try:
        resp = requests.get(url, timeout=10)
        img = Image.open(io.BytesIO(resp.content)).convert("RGB").resize(size)
        img.save(path, "JPEG")
    except:
        img = Image.new("RGB", size, (10, 10, 20))
        img.save(path, "JPEG")

# --- واجهة المستخدم (التصميم الهندسي) ---
st.set_page_config(page_title="Mediawy V102 Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #050a0f; color: #e0e0e0; }
    .css-1kyx60p { background-color: #0d1117; border-right: 1px solid #00E5FF; }
    .render-box { border: 2px solid #00E5FF; padding: 25px; border-radius: 20px; background: #0d1117; box-shadow: 0 0 15px #00E5FF33; }
    h1, h2, h3 { color: #00E5FF !important; }
    </style>
""", unsafe_allow_html=True)

# --- توزيع الأعمدة (الإضافات على الجانبين والإنتاج في المنتصف) ---
left_col, mid_col, right_col = st.columns([1, 1.8, 1])

# --- الجانب الأيسر (المدخلات الأساسية) ---
with left_col:
    st.subheader("📏 1. الأبعاد والمنصة")
    platform = st.selectbox("نوع الفيديو:", ["Shorts/TikTok (9:16)", "YouTube (16:9)", "Facebook/Post (1:1)"])
    st.divider()
    
    st.subheader("🎙️ 2. التعليق الصوتي")
    v_mode = st.radio("اختر المصدر:", ["AI 🤖", "ElevenLabs 💎", "بشري 🎤"])
    if v_mode == "AI 🤖":
        v_text = st.text_area("نص الـ AI:")
    elif v_mode == "ElevenLabs 💎":
        el_api = st.text_input("🔑 API Key")
        el_model = st.text_input("📦 Model ID")
        v_text = st.text_area("📝 نص ElevenLabs:")
    else:
        u_voice = st.file_uploader("📥 ارفع صوتك (MP3)")
        v_text = st.text_area("📝 النص (للمزامنة):")
    st.divider()

    st.subheader("🖼️ 3. الصور والأجواء")
    img_type = st.radio("مصدر الصور:", ["أوتوماتيك ✨", "يدوي 📁"])
    if img_type == "يدوي 📁":
        u_imgs = st.file_uploader("ارفع الصور:", accept_multiple_files=True)
    else:
        img_keywords = st.text_input("مربع الكلمات المفتاحية:")

# --- الجانب الأيمن (الإضافات والـ SEO) ---
with right_col:
    st.subheader("🎭 4. نمط المونتاج")
    m_style = st.selectbox("اختر الروح العامة:", ["سينمائي 🎬", "درامي 🎭", "وثائقي 🎞️"])
    st.divider()

    st.subheader("🎵 5. الموسيقى")
    bg_music = st.radio("تراك الخلفية:", ["أوتوماتيك 🎹", "يدوي 🎷"])
    u_bg = st.file_uploader("ارفع الموسيقى:") if bg_music == "يدوي 🎷" else None
    st.divider()

    st.subheader("🎨 6. الهوية والبصمة")
    show_subs = st.toggle("ترجمة كلمة بكلمة", value=True)
    show_banner = st.toggle("بنر سفلي احترافي")
    use_logo = st.toggle("إضافة لوجو")
    u_logo = st.file_uploader("شعارك:") if use_logo else None
    st.divider()

    st.subheader("📝 7. ملخص الـ SEO")
    show_seo = st.toggle("توليد بيانات الفيديو")

# --- العمود الأوسط (غرفة الرندر والإنتاج) ---
with mid_col:
    st.markdown("<div class='render-box'>", unsafe_allow_html=True)
    st.header("📺 استوديو الإنتاج المركزي")
    
    if st.button("🚀 بدء صناعة الفيلم (V102)"):
        try:
            with st.spinner(f"جاري معالجة فيديو {m_style}..."):
                # 1. الصوت
                audio_p = os.path.join(ASSETS_DIR, "voice.mp3")
                if v_mode == "بشري 🎤" and u_voice:
                    with open(audio_p, "wb") as f: f.write(u_voice.getbuffer())
                else:
                    gTTS(v_text, lang='ar').save(audio_p)
                voice = AudioFileClip(audio_p)
                
                # 2. الأبعاد
                if "9:16" in platform: w, h = 1080, 1920
                elif "16:9" in platform: w, h = 1920, 1080
                else: w, h = 1080, 1080

                # 3. المشاهد
                sentences = [s.strip() for s in re.split(r'[.؟!،]+', v_text) if len(s.strip()) > 1]
                dur_scene = voice.duration / len(sentences)
                
                img_clips = []
                for i, sent in enumerate(sentences):
                    p = os.path.join(ASSETS_DIR, f"p_{i}.jpg")
                    if img_type == "أوتوماتيك ✨":
                        get_cinematic_image(sent + " " + img_keywords, p, (w, h), m_style)
                    else:
                        with open(p, "wb") as f: f.write(u_imgs[i % len(u_imgs)].getbuffer())
                    
                    c = ImageClip(p).with_duration(dur_scene + 0.5)
                    # تعديل الزووم حسب النمط
                    z_val = 1.2 if m_style == "سينمائي 🎬" else 1.1
                    c = c.resized(lambda t: 1 + (z_val-1) * (t / dur_scene))
                    img_clips.append(c)

                video = concatenate_videoclips(img_clips, method="compose", padding=-0.4)
                
                # 4. الرندر النهائي
                final_path = os.path.join(VIDEOS_DIR, "Mediawy_Ultra.mp4")
                video.with_audio(voice).write_videofile(final_path, fps=24, codec="libx264")
                
                st.video(final_path)
                st.success(f"✅ تم إنتاج الفيلم بنمط {m_style}")

                if show_seo:
                    st.divider()
                    st.markdown(f"### 📑 ملخص الإنتاج:\n**الاسم:** {sentences[0]}\n**الكلمات:** {img_keywords}\n**الوصف:** فيلم {m_style} احترافي.")

        except Exception as e:
            st.error(f"خطأ: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
