import streamlit as st
import os, requests, re, io, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip, vfx

# --- 1. إعداد البيئة ---
MEDIA_DIR = "Mediawy_Final_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- دالة صنع البنر الاحترافي ---
def create_pro_banner(size, text):
    w, h = size
    banner_h = int(h * 0.1) # البنر بياخد 10% من طول الفيديو
    banner = Image.new("RGBA", (w, banner_h), (0, 0, 0, 160)) # شفافية سوداء سينمائية
    draw = ImageDraw.Draw(banner)
    try: font = ImageFont.truetype("arial.ttf", banner_h // 2)
    except: font = ImageFont.load_default()
    
    # رسم خط علوي للبنر ليعطي شكل فني
    draw.line([(0, 0), (w, 0)], fill="#007BFF", width=3)
    draw.text((w // 2, banner_h // 2), text, font=font, fill="white", anchor="mm")
    
    path = os.path.join(ASSETS_DIR, "banner_live.png")
    banner.save(path)
    return path

# --- واجهة المستخدم البيضاء بالكامل ---
st.set_page_config(page_title="Mediawy V107 Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #1e1e1e; }
    .render-zone { border: 2px solid #007BFF; padding: 20px; border-radius: 15px; background-color: #f9f9f9; }
    h2 { color: #007BFF !important; border-bottom: 2px solid #007BFF; }
    </style>
""", unsafe_allow_html=True)

col_right, col_mid, col_left = st.columns([1, 1.8, 1])

with col_right:
    st.markdown("## 📏 1. الأبعاد")
    platform = st.selectbox("المقاس:", ["Shorts (9:16)", "YouTube (16:9)", "Post (1:1)"])
    st.divider()
    st.markdown("## 🎙️ 2. هندسة الصوت")
    v_src = st.radio("المصدر:", ["AI 🤖", "ElevenLabs 💎", "بشري 🎤"])
    voice_text = st.text_area("✍️ جدول النص:")

with col_left:
    st.markdown("## 🎭 3. النمط")
    m_style = st.selectbox("الروح:", ["سينمائي 🎬", "درامي 🎭", "وثائقي 🎞️"])
    st.divider()
    st.markdown("## 🎨 4. الهوية (اللوجو والبنر)")
    use_logo = st.toggle("إضافة لوجو (سيظهر بالأعلى)")
    u_logo = st.file_uploader("📥 ارفع اللوجو هنا") if use_logo else None
    
    use_banner = st.toggle("تفعيل البنر السفلي")
    banner_text = st.text_input("نص البنر (اختياري):", value="Mediawy AI Studio") if use_banner else ""
    st.divider()
    img_opt = st.radio("الصور:", ["أوتو", "يدوي"])
    u_imgs = st.file_uploader("ارفع الصور", accept_multiple_files=True) if img_opt == "يدوي" else None

with col_mid:
    st.markdown("<div class='render-zone'>", unsafe_allow_html=True)
    st.subheader("📺 منطقة الإنتاج")
    
    if st.button("🚀 رندر الفيديو (إصلاح اللوجو)"):
        try:
            with st.spinner("جاري دمج الطبقات (الصور + اللوجو + البنر)..."):
                # معالجة الصوت
                v_p = os.path.join(ASSETS_DIR, "v.mp3")
                gTTS(voice_text, lang='ar').save(v_p)
                voice = AudioFileClip(v_p)
                
                # الأبعاد
                if "9:16" in platform: w, h = 1080, 1920
                else: w, h = 1920, 1080

                # بناء الفيديو الأساسي
                sentences = [s.strip() for s in re.split(r'[.؟!،]+', voice_text) if len(s.strip()) > 1]
                dur = voice.duration / len(sentences)
                
                # 
                
                clips = []
                for i, sent in enumerate(sentences):
                    img_p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
                    # (كود جلب الصور هنا...)
                    resp = requests.get(f"https://picsum.photos/seed/{i}/{w}/{h}")
                    Image.open(io.BytesIO(resp.content)).save(img_p)
                    
                    c = ImageClip(img_p).with_duration(dur).resized(lambda t: 1 + 0.1 * (t / dur))
                    clips.append(c)
                
                video_track = concatenate_videoclips(clips, method="compose")

                # --- نظام الطبقات (Overlays) ---
                layers = [video_track]
                
                # 1. إضافة البنر (في الأسفل)
                if use_banner:
                    b_path = create_pro_banner((w, h), banner_text)
                    banner_clip = ImageClip(b_path).with_duration(voice.duration).with_position(("center", "bottom"))
                    layers.append(banner_clip)

                # 2. إضافة اللوجو (فوق كل شيء في الزاوية)
                if use_logo and u_logo:
                    l_p = os.path.join(ASSETS_DIR, "user_logo.png")
                    logo_img = Image.open(u_logo).convert("RGBA")
                    logo_img.thumbnail((w // 6, h // 6)) # تصغير اللوجو بنسبة متناسقة
                    logo_img.save(l_p)
                    logo_clip = ImageClip(l_p).with_duration(voice.duration).with_position((w - (w//6) - 20, 20))
                    layers.append(logo_clip)

                final_video = CompositeVideoClip(layers, size=(w, h)).with_audio(voice)
                out = os.path.join(VIDEOS_DIR, "Final_V107.mp4")
                final_video.write_videofile(out, fps=24, codec="libx264")
                
                st.video(out)
                st.success("🎯 تم الرندر واللوجو ظاهر الآن!")
                
        except Exception as e:
            st.error(f"خطأ: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
