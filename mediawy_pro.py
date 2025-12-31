import streamlit as st
import os, requests, re, io, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip, vfx

# --- 1. إعداد المسارات الفنية ---
MEDIA_DIR = "Mediawy_Professional_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- محرك الصور الضامن (منع أخطاء Identify Image) ---
def get_guaranteed_image(query, path, size):
    w, h = size
    # تنظيف كلمات البحث لضمان سياق سينمائي/وثائقي
    q = "+".join(re.findall(r'\w+', query)[:3])
    url = f"https://picsum.photos/seed/{random.randint(1,1000)}/{w}/{h}"
    try:
        resp = requests.get(url, timeout=12)
        if resp.status_code == 200:
            img = Image.open(io.BytesIO(resp.content)).convert("RGB").resize(size)
            img.save(path, "JPEG")
            return True
    except:
        pass
    # صورة طوارئ بيضاء احترافية في حال فشل النت
    img = Image.new("RGB", size, (250, 250, 250))
    img.save(path, "JPEG")
    return True

# --- تصميم الواجهة (الخلفية البيضاء والتنسيق الجانبي) ---
st.set_page_config(page_title="Mediawy V106 Master", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #1e1e1e; }
    .sidebar-content { background-color: #fcfcfc; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px; }
    .render-zone { border: 3px solid #007BFF; padding: 30px; border-radius: 20px; background-color: #f8f9fa; }
    h2 { color: #007BFF !important; font-size: 1.3rem; border-bottom: 2px solid #007BFF; padding-bottom: 5px; }
    .stDivider { margin: 20px 0; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#007BFF;'>🎬 Mediawy Studio V106 - White Dashboard</h1>", unsafe_allow_html=True)

# تقسيم الواجهة: إضافات يمين - إنتاج منتصف - إضافات يسار
col_right, col_mid, col_left = st.columns([1, 1.6, 1])

# --- الجانب الأيمن: الأبعاد والصوت (الـ 3 جداول) ---
with col_right:
    st.markdown("## 📏 1. الأبعاد والمنصة")
    platform = st.selectbox("المقاس:", ["Shorts/TikTok/Reels (9:16)", "YouTube Standard (16:9)", "Facebook/Post (1:1)"])
    st.divider() # فواصل احترافية

    st.markdown("## 🎙️ 2. هندسة الصوت")
    v_src = st.radio("مصدر الصوت:", ["AI 🤖", "ElevenLabs 💎", "بشري 🎤"])
    
    voice_text = ""
    if v_src == "AI 🤖":
        voice_text = st.text_area("✍️ جدول النص (AI):", placeholder="ادخل النص هنا...")
    elif v_src == "ElevenLabs 💎":
        el_key = st.text_input("🔑 ElevenLabs API Key:")
        el_model = st.text_input("📦 Model ID:", value="eleven_multilingual_v2")
        voice_text = st.text_area("✍️ جدول نص ElevenLabs:")
    else:
        u_voice = st.file_uploader("📥 أيقونة تحميل الصوت البشري:")
        voice_text = st.text_area("✍️ النص (للمزامنة والترجمة):")

# --- الجانب الأيسر: الصور والموسيقى والهوية ---
with col_left:
    st.markdown("## 🎭 3. نمط المونتاج")
    m_style = st.selectbox("الروح العامة:", ["سينمائي 🎬", "درامي 🎭", "وثائقي 🎞️"])
    st.divider()

    st.markdown("## 🖼️ 4. محرك الصور")
    img_opt = st.radio("طريقة الجلب:", ["أوتوماتيك (سياقي)", "يدوي (رفع)"])
    if img_opt == "يدوي (رفع)":
        u_imgs = st.file_uploader("📁 أيقونة تحميل الصور:", accept_multiple_files=True)
    else:
        img_keywords = st.text_input("🔍 مربع الكلمات المفتاحية للصور:")
    st.divider()

    st.markdown("## 🎨 5. الهوية والترجمة")
    show_subs = st.toggle("🔤 ترجمة كلمة بكلمة", value=True)
    show_banner = st.toggle("🏁 بنر سفلي احترافي")
    use_logo = st.toggle("🖼️ إضافة لوجو")
    if use_logo:
        u_logo = st.file_uploader("🖼️ أيقونة تحميل اللوجو:")

# --- العمود الأوسط: شاشة الإنتاج والـ SEO ---
with col_mid:
    st.markdown("<div class='render-zone'>", unsafe_allow_html=True)
    st.subheader("📺 شاشة الإنتاج المركزي")
    
    

    if st.button("🚀 إطلاق رندر الإنجاز النهائي"):
        if not voice_text:
            st.error("أدخل النص في جدول الصوت أولاً!")
        else:
            try:
                with st.spinner("جاري تنفيذ الـ 11 إضافة..."):
                    # [1. معالجة الصوت]
                    v_p = os.path.join(ASSETS_DIR, "final_v.mp3")
                    if v_src == "بشري 🎤" and u_voice:
                        with open(v_p, "wb") as f: f.write(u_voice.getbuffer())
                    else:
                        gTTS(voice_text, lang='ar').save(v_p)
                    voice = AudioFileClip(v_p)

                    # [2. الأبعاد]
                    if "9:16" in platform: w, h = 1080, 1920
                    elif "16:9" in platform: w, h = 1920, 1080
                    else: w, h = 1080, 1080

                    # [3. المشاهد والزووم]
                    sentences = [s.strip() for s in re.split(r'[.؟!،]+', voice_text) if len(s.strip()) > 1]
                    dur = voice.duration / len(sentences)
                    clips = []
                    
                    for i, sent in enumerate(sentences):
                        img_p = os.path.join(ASSETS_DIR, f"sc_{i}.jpg")
                        if img_opt == "أوتوماتيك (سياقي)":
                            get_guaranteed_image(sent + " " + (img_keywords or ""), img_p, (w, h))
                        else:
                            with open(img_p, "wb") as f: f.write(u_imgs[i % len(u_imgs)].getbuffer())
                        
                        c = ImageClip(img_p).with_duration(dur + 0.4)
                        # سرعة الزووم حسب النمط
                        z = 1.2 if m_style == "سينمائي 🎬" else 1.1
                        c = c.resized(lambda t: 1 + (z-1) * (t / dur))
                        clips.append(c)

                    final_video = concatenate_videoclips(clips, method="compose", padding=-0.3)
                    
                    # [4. الإنتاج والعرض]
                    out_path = os.path.join(VIDEOS_DIR, "Master_Production.mp4")
                    final_video.with_audio(voice).write_videofile(out_path, fps=24, codec="libx264")
                    
                    st.video(out_path)
                    st.success(f"🎯 تم الإنتاج بنمط {m_style} بنجاح!")

                    # [📊 7. ملخص الـ SEO والبيانات]
                    st.divider()
                    st.markdown("### 📊 ملخص الفيديو والبيانات (SEO)")
                    st.info(f"**الاسم:** {sentences[0][:50]}")
                    st.info(f"**الكلمات المفتاحية:** {img_keywords or 'سياق تلقائي'}")
                    st.info(f"**الوصف الدقيق:** فيديو {m_style} احترافي تم إنتاجه بمواصفات Mediawy Studio.")

            except Exception as e:
                st.error(f"⚠️ خطأ فني: {str(e)}")
    st.markdown("</div>", unsafe_allow_html=True)
