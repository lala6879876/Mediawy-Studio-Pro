import streamlit as st
import os
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import re

# --- 1. الاستدعاء الاحترافي (MoviePy 2.x) ---
import moviepy as mp
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip

if os.name == 'posix': 
    os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"

# --- 2. إعداد المجلدات ---
MEDIA_DIR = "Mediawy_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- 3. محرك الكتابة (Subtitles) والبنر ---
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

def create_static_layer(size, logo_path, banner_text):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("arial.ttf", size[1] // 25)
    except: font = ImageFont.load_default()
    if banner_text:
        draw.rectangle([0, size[1]-100, size[0], size[1]], fill=(0,0,0,200))
        draw.text((40, size[1]-75), banner_text, font=font, fill="white")
    if logo_path:
        logo = Image.open(logo_path).convert("RGBA").resize((size[0]//6, size[0]//6))
        img.paste(logo, (size[0]-size[0]//6-30, 30), logo)
    return ImageClip(np.array(img))

# --- 4. واجهة المستخدم (الـ 11 إضافة) ---
st.set_page_config(page_title="Mediawy V47", layout="wide")
st.markdown("<h1 style='text-align:center; color:#FF0000;'>🎬 Mediawy Studio <span style='color:#00E5FF;'>V47 Shield</span></h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ مركز التحكم")
    dim = st.selectbox("📏 الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    edit_style = st.selectbox("🎭 النمط الفني:", ["سينمائي 🎬", "درامي 🎭", "وثائقي 📜"])
    ai_text = st.text_area("✍️ النص (حتى 500 كلمة):", height=150)
    img_mode = st.radio("الجلب:", ["أوتوماتيك (AI)", "يدوي (رفع)"])
    user_imgs = st.file_uploader("ارفع صورك", accept_multiple_files=True)
    logo_file = st.file_uploader("ارفع اللوجو")
    marquee_text = st.text_input("نص البنر السفلي:")

# --- 5. محرك الرندر المصلح ---
if st.button("🚀 إطلاق خط الإنتاج المصلح", use_container_width=True):
    if not ai_text or not logo_file:
        st.error("⚠️ يرجى كتابة النص ورفع اللوجو!")
    else:
        try:
            status = st.info("⏳ جاري المعالجة الآمنة للصور...")
            
            # معالجة الصوت
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
                
                # جلب البيانات
                if "أوتوماتيك" in img_mode:
                    img_data = requests.get(f"https://images.unsplash.com/photo-1500000000000?w={w}&h={h}&q=80").content
                    with open(p, "wb") as fo: fo.write(img_data)
                elif user_imgs:
                    with open(p, "wb") as fo: fo.write(user_imgs[i % len(user_imgs)].getbuffer())
                
                # الكود المنقذ: فتح الصورة بـ Pillow يدوياً لمنع خطأ الـ Backend
                with Image.open(p) as pil_img:
                    # تحويل لـ RGB وتعديل الحجم لضمان التوافق
                    pil_img = pil_img.convert("RGB").resize((w, h))
                    img_array = np.array(pil_img)
                
                # إنشاء الكليب من المصفوفة مباشرة
                c = ImageClip(img_array).with_duration(dur_per_clip)
                z = 1.25 if i % 2 == 0 else 0.85
                c = c.resized(lambda t: 1 + (z-1) * (t / dur_per_clip)).with_crossfadein(0.5)
                
                img_clips.append(c)
                sub_clips.append(create_word_clip((w, h), sentence, i*dur_per_clip, dur_per_clip))

            video_track = concatenate_videoclips(img_clips, method="compose")
            
            l_p = os.path.join(ASSETS_DIR, "l.png")
            with open(l_p, "wb") as f: f.write(logo_file.getbuffer())
            static_layer = create_static_layer((w, h), l_p, marquee_text).with_duration(total_dur)

            final_vid = CompositeVideoClip([video_track, static_layer] + sub_clips, size=(w, h)).with_audio(voice_clip)
            
            out_p = os.path.join(VIDEOS_DIR, "Final_Shield.mp4")
            final_vid.write_videofile(out_p, fps=24, codec="libx264")
            
            st.video(out_p)
            st.success("🔥 مبروك! المصنع اشتغل وتخطى خطأ الـ Backend!")
            
        except Exception as e: st.error(f"⚠️ خطأ فني: {str(e)}")
