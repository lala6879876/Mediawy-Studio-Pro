import streamlit as st
import os
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import re

# --- 1. الاستدعاء الحديث لـ MoviePy 2.x (حل كل المشاكل السابقة) ---
from moviepy.video.VideoClip import ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

# ضبط محرك الصور
if os.name == 'posix': os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"
else: os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"

# --- 2. إعداد المجلدات ---
BASE_PATH = os.getcwd()
MEDIA_DIR = os.path.join(BASE_PATH, "Mediawy_Studio")
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- 3. محركات الرسم والذكاء (ثبات العناصر + الفلاتر) ---
def create_static_layer(size, logo_path, marquee_text):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("arial.ttf", size[1] // 25)
    except: font = ImageFont.load_default()
    if marquee_text:
        draw.rectangle([0, size[1]-80, size[0], size[1]], fill=(0,0,0,180))
        draw.text((40, size[1]-65), marquee_text, font=font, fill="white")
    if logo_path:
        logo = Image.open(logo_path).convert("RGBA").resize((size[0]//6, size[0]//6))
        img.paste(logo, (size[0]-size[0]//6-30, 30), logo)
    return ImageClip(np.array(img))

def create_text_clip(size, text, start_t, dur):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("arial.ttf", size[1] // 15)
    except: font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    draw.rectangle([size[0]//2-tw//2-20, size[1]//2-th//2-10, size[0]//2+tw//2+20, size[1]//2+th//2+10], fill=(0,0,0,160))
    draw.text((size[0]//2-tw//2, size[1]//2-th//2), text, font=font, fill="yellow")
    return ImageClip(np.array(img)).with_start(start_t).with_duration(dur).with_position('center')

# --- 4. واجهة المستخدم الفخمة ---
st.set_page_config(page_title="Mediawy Mega V32", layout="wide")
st.markdown("<h1 style='text-align:center; color:#e60000;'>Mediawy Studio <span style='color:#00e5ff;'>V32 The Beast</span></h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ مركز التحكم")
    dim = st.selectbox("📏 1. الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    edit_style = st.selectbox("🎭 2. النمط الفني:", ["سينمائي", "درامي", "وثائقي"])
    st.markdown("---")
    audio_source = st.radio("🎤 3. الصوت:", ["بشري", "AI (GTTS)", "ElevenLabs"])
    el_key = st.text_input("ElevenLabs Key", type="password") if audio_source == "ElevenLabs" else ""
    el_voice = st.text_input("Voice ID", value="pNInz6obpgnu9P6ky9M8") if audio_source == "ElevenLabs" else ""
    ai_text = st.text_area("النص (حتى 500 كلمة):", height=150)
    user_audio = st.file_uploader("ارفع الصوت البشري")
    st.markdown("---")
    bg_music_opt = st.toggle("🎵 4. موسيقى + Ducking", value=True)
    ducking_strength = st.slider("🔇 قوة خفض الموسيقى:", 0.05, 0.4, 0.1)
    st.markdown("---")
    img_mode = st.radio("🖼️ 5. الصور:", ["سياق أوتوماتيك AI", "يدوي (بشرى)"])
    user_imgs = st.file_uploader("ارفع حتى 500 صورة", accept_multiple_files=True)
    st.markdown("---")
    marquee_text = st.text_input("🎞️ 6. نص البنر:", "Mediawy Studio 2026")
    logo_file = st.file_uploader("🚩 7. ارفع اللوجو")

# --- 5. محرك الإنتاج الشامل ---
if st.button("إطلاق خط الإنتاج الشامل 🚀", use_container_width=True):
    if not (ai_text or user_audio) or not logo_file:
        st.error("⚠️ ناقص بيانات!")
    else:
        try:
            status = st.info("🎙️ جاري هندسة الصوت وتحليل السياق...")
            audio_p = os.path.join(ASSETS_DIR, "v.mp3")
            if audio_source == "ElevenLabs":
                res = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{el_voice}", json={"text": ai_text}, headers={"xi-api-key": el_key})
                with open(audio_p, "wb") as f: f.write(res.content)
            elif audio_source == "AI (GTTS)": gTTS(ai_text, lang='ar').save(audio_p)
            else: 
                with open(audio_p, "wb") as f: f.write(user_audio.getbuffer())
            
            voice_clip = AudioFileClip(audio_p)
            total_dur = voice_clip.duration

            sentences = [s.strip() for s in re.split(r'[.؟!،,]+', ai_text) if len(s.strip()) > 3]
            num_clips = len(sentences)
            dur_per_clip = total_dur / num_clips if num_clips > 0 else total_dur

            h = 1080; w = int(h*9/16) if "9:16" in dim else int(h*16/9)
            img_clips = []
            sub_clips = []

            for i, sentence in enumerate(sentences):
                p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
                if img_mode == "سياق أوتوماتيك AI":
                    search = sentence.split()[0] if sentence.split() else "nature"
                    img_data = requests.get(f"https://images.unsplash.com/photo-1500000000000?w={w}&h={h}&q=80").content
                    with open(p, "wb") as fo: fo.write(img_data)
                else:
                    with open(p, "wb") as fo: fo.write(user_imgs[i % len(user_imgs)].getbuffer())
                
                c = ImageClip(p).with_duration(dur_per_clip).resized(height=h)
                # فلاتر النمط
                if edit_style == "درامي": c = c.with_effects([lambda cl: cl.image_transform(lambda im: (im * 0.7).astype('uint8'))])
                
                # زووم ناعم (Ken Burns)
                z = 1.15 if i % 2 == 0 else 0.85
                c = c.resized(lambda t: 1 + (z-1) * (t/dur_per_clip))
                img_clips.append(c)
                sub_clips.append(create_text_clip((w, h), sentence, i*dur_per_clip, dur_per_clip))

            video_track = concatenate_videoclips(img_clips, method="compose")

            l_p = os.path.join(ASSETS_DIR, "l.png")
            with open(l_p, "wb") as f: f.write(logo_file.getbuffer())
            static_layer = create_static_layer((w, h), l_p, marquee_text).with_duration(total_dur)

            # Ducking
            if bg_music_opt:
                bg = AudioFileClip("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3").with_duration(total_dur).with_volume_scaled(ducking_strength)
                final_audio = CompositeAudioClip([voice_clip.with_volume_scaled(1.2), bg])
            else: final_audio = voice_clip

            final_vid = CompositeVideoClip([video_track, static_layer] + sub_clips, size=(w, h)).with_audio(final_audio)
            out_p = os.path.join(VIDEOS_DIR, "Mediawy_V32.mp4")
            final_vid.write_videofile(out_p, fps=24, codec="libx264")
            
            st.video(out_p)
            st.success("🔥 المكنة طلعت قماش كامل وبكل الإضافات!")
            st.subheader("📋 بيانات SEO")
            st.code(f"عنوان مقترح: {sentences[0] if sentences else 'فيديو جديد'}\n#Mediawy_Studio #AI #Shorts")

        except Exception as e: st.error(f"⚠️ خطأ: {str(e)}")
