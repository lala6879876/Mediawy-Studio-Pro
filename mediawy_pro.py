import streamlit as st
import os
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import re

# --- 1. الاستدعاءات الحديثة (MoviePy 2.x) ---
import moviepy as mp
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip

if os.name == 'posix': 
    os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"

# --- 2. إعداد المجلدات ---
MEDIA_DIR = "Mediawy_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- 3. محرك الصور الذكي (صمام الأمان) ---
def get_safe_image(path, size):
    """فحص الصورة واستبدالها بصورة ملونة في حال التلف"""
    try:
        with Image.open(path) as img:
            img.verify() # التأكد من سلامة الملف
        img = Image.open(path).convert("RGB").resize(size)
        return np.array(img)
    except Exception as e:
        # لو الصورة تالفة، بنرسم خلفية ملونة عشان المكنة متقفش
        st.warning(f"⚠️ تم رصد صورة تالفة، تم استبدالها بخلفية سينمائية.")
        dummy = Image.new("RGB", size, (30, 30, 30))
        draw = ImageDraw.Draw(dummy)
        draw.text((size[0]//4, size[1]//2), "Mediawy Studio - Image Error", fill="gray")
        return np.array(dummy)

# --- 4. محرك النصوص والهوية ---
def create_word_clip(size, text, start_t, dur):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("arial.ttf", size[1] // 18)
    except: font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    y_pos = int(size[1] * 0.75) - (th // 2)
    x_pos = (size[0] // 2) - (tw // 2)
    draw.rectangle([x_pos-20, y_pos-10, x_pos+tw+20, y_pos+th+10], fill=(0,0,0,180))
    draw.text((x_pos, y_pos), text, font=font, fill="yellow")
    return ImageClip(np.array(img)).with_start(start_t).with_duration(dur)

# --- 5. واجهة المستخدم (الـ 11 إضافة) ---
st.set_page_config(page_title="Mediawy V48", layout="wide")
st.markdown("<h1 style='text-align:center; color:#FF0000;'>🎬 Mediawy Studio <span style='color:#00E5FF;'>V48 Smart Filter</span></h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ مركز التحكم")
    dim = st.selectbox("📏 الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    ai_text = st.text_area("✍️ النص (حتى 500 كلمة):", height=150)
    img_mode = st.radio("جلب الصور:", ["أوتوماتيك (سياق AI)", "يدوي (رفع)"])
    user_imgs = st.file_uploader("ارفع صورك", accept_multiple_files=True)
    logo_file = st.file_uploader("ارفع اللوجو")
    marquee_text = st.text_input("نص البنر السفلي:")

# --- 6. محرك الرندر المنقذ ---
if st.button("🚀 إطلاق خط الإنتاج المصلح", use_container_width=True):
    if not ai_text or not logo_file:
        st.error("⚠️ يرجى إكمال البيانات الأساسية!")
    else:
        try:
            status = st.info("⏳ جاري المونتاج مع نظام الفلترة الذكي...")
            
            audio_p = os.path.join(ASSETS_DIR, "v.mp3")
            gTTS(ai_text, lang='ar').save(audio_p)
            voice_clip = AudioFileClip(audio_p)
            total_dur = voice_clip.duration

            sentences = [s.strip() for s in re.split(r'[.؟!،,]+', ai_text) if len(s.strip()) > 2]
            dur_per_clip = total_dur / len(sentences)

            h = 1080; w = int(h*9/16) if "9:16" in dim else int(h*16/9)
            img_clips = []
            sub_clips = []

            for i, sentence in enumerate(sentences):
                p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
                
                if "أوتوماتيك" in img_mode:
                    # سحب صورة من رابط مباشر ومضمون
                    img_data = requests.get(f"https://picsum.photos/seed/{i}/{w}/{h}").content
                    with open(p, "wb") as fo: fo.write(img_data)
                elif user_imgs:
                    with open(p, "wb") as fo: fo.write(user_imgs[i % len(user_imgs)].getbuffer())
                
                # استخدام الفلتر الذكي لجلب الصورة كمصفوفة
                img_array = get_safe_image(p, (w, h))
                
                c = ImageClip(img_array).with_duration(dur_per_clip)
                z = 1.25 if i % 2 == 0 else 0.85
                c = c.resized(lambda t: 1 + (z-1) * (t / dur_per_clip)).with_crossfadein(0.5)
                
                img_clips.append(c)
                sub_clips.append(create_word_clip((w, h), sentence, i*dur_per_clip, dur_per_clip))

            video_track = concatenate_videoclips(img_clips, method="compose")
            
            l_p = os.path.join(ASSETS_DIR, "l.png")
            with open(l_p, "wb") as f: f.write(logo_file.getbuffer())
            
            # الهوية والدمج
            final_vid = CompositeVideoClip([video_track] + sub_clips, size=(w, h)).with_audio(voice_clip)
            
            out_p = os.path.join(VIDEOS_DIR, "Final_Stable.mp4")
            final_vid.write_videofile(out_p, fps=24, codec="libx264")
            
            st.video(out_p)
            st.success("🔥 المكنة رجعت تشتغل وبقوة!")
            
        except Exception as e: st.error(f"⚠️ خطأ فني: {str(e)}")
