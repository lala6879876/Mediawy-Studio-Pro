import streamlit as st
import os
import time
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import re

# --- 1. حلول الاستقرار الجذري ---
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except:
    pass

from moviepy.editor import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip

# --- 2. إعداد المجلدات ---
BASE_PATH = os.getcwd()
MEDIA_DIR = os.path.join(BASE_PATH, "Mediawy_Studio")
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- 3. محرك الرسم والذكاء (ثبات العناصر + الفلاتر) ---
def process_static_layer(size, logo_path, marquee_text):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("arial.ttf", size[1] // 25)
    except: font = ImageFont.load_default()
    if marquee_text:
        draw.rectangle([0, size[1]-80, size[0], size[1]], fill=(0,0,0,180))
        draw.text((40, size[1]-65), marquee_text, font=font, fill="white")
    if logo_path:
        logo = Image.open(logo_path).convert("RGBA").resize((size[0]//6, size[0]//6))
        img.paste(logo, (size[0] - size[0]//6 - 30, 30), logo)
    return ImageClip(np.array(img))

def create_text_clip(size, text, start_t, end_t):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("arial.ttf", size[1] // 15)
    except: font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.rectangle([size[0]//2 - tw//2 - 20, size[1]//2 - th//2 - 10, 
                    size[0]//2 + tw//2 + 20, size[1]//2 + th//2 + 10], fill=(0,0,0,160))
    draw.text((size[0]//2 - tw//2, size[1]//2 - th//2), text, font=font, fill="yellow")
    return ImageClip(np.array(img)).set_start(start_t).set_end(end_t).set_position('center')

# --- 4. واجهة المستخدم المنظمة ---
st.set_page_config(page_title="Mediawy Mega V15", layout="wide")
st.markdown("<h1 style='text-align:center; color:#e60000;'>Mediawy Studio <span style='color:#00e5ff;'>V15 The Beast</span></h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ مركز التحكم")
    dim = st.selectbox("📏 1. الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    edit_style = st.selectbox("🎭 2. النمط الفني:", ["سينمائي", "درامي", "وثائقي"])
    st.markdown("---")
    
    audio_source = st.radio("🎤 3. مصدر الصوت:", ["بشري", "AI (GTTS)", "ElevenLabs"])
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
    
    marquee_text = st.text_input("🎞️ 6. نص البنر السفلي:", "Mediawy Studio")
    logo_file = st.file_uploader("🚩 7. ارفع اللوجو")

# --- 5. محرك الإنتاج الشامل ---
if st.button("إطلاق خط الإنتاج الشامل 🚀", use_container_width=True):
    if not (ai_text or user_audio) or not logo_file:
        st.error("⚠️ ناقص بيانات (النص واللوجو)!")
    else:
        try:
            # أ- الصوت
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

            # ب- تقسيم السياق والمزامنة
            sentences = re.split(r'[.؟!،,]+', ai_text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 3]
            num_clips = len(sentences)
            dur_per_clip = total_dur / num_clips

            # ج- المونتاج (زووم الصور وفلاتر الألوان)
            h = 1080; w = int(h*9/16) if "9:16" in dim else int(h*16/9)
            img_clips = []
            sub_clips = []

            for i, sentence in enumerate(sentences):
                p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
                if img_mode == "سياق أوتوماتيك AI":
                    keywords = [w for w in sentence.split() if len(w) > 3]
                    search = keywords[0] if keywords else "abstract"
                    img_data = requests.get(f"https://source.unsplash.com/featured/{w}x{h}/?{search}").content
                    with open(p, "wb") as fo: fo.write(img_data)
                else:
                    with open(p, "wb") as fo: fo.write(user_imgs[i % len(user_imgs)].getbuffer())
                
                c = ImageClip(p).set_duration(dur_per_clip).resize(height=h).set_position('center')
                # فلاتر النمط
                if edit_style == "درامي": c = c.fx(lambda clip: clip.image_transform(lambda im: (im * 0.7).astype('uint8')))
                elif edit_style == "سينمائي": c = c.fx(lambda clip: clip.image_transform(lambda im: (im * 1.2).astype('uint8')))
                
                # زووم متناوب
                z = 1.15 if i % 2 == 0 else 0.85
                c = c.resize(lambda t: 1 + (z-1) * (t/dur_per_clip)).crossfadein(0.5)
                img_clips.append(c)
                sub_clips.append(create_text_clip((w, h), sentence, i*dur_per_clip, (i+1)*dur_per_clip))

            video_track = concatenate_videoclips(img_clips, method="compose")

            # د- الطبقات الثابتة (اللوجو والبنر)
            l_p = os.path.join(ASSETS_DIR, "l.png")
            with open(l_p, "wb") as f: f.write(logo_file.getbuffer())
            static_layer = process_static_layer((w, h), l_p, marquee_text).set_duration(total_dur)

            # هـ- الصوت النهائي (Ducking)
            if bg_music_opt:
                bg = AudioFileClip("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3").volumex(ducking_strength).set_duration(total_dur)
                final_audio = CompositeAudioClip([voice_clip.volumex(1.2), bg])
            else: final_audio = voice_clip

            # الرندر النهائي
            final_vid = CompositeVideoClip([video_track, static_layer] + sub_clips, size=(w, h)).set_audio(final_audio)
            out_p = os.path.join(VIDEOS_DIR, "Mediawy_Beast_V15.mp4")
            final_vid.write_videofile(out_p, fps=24, codec="libx264")
            
            st.video(out_p)
            st.success("🔥 مبروك! المكنة طلعت قماش كاااامل وبالسياق الصحيح!")
            st.subheader("📋 11. بيانات SEO")
            st.code(f"الاسم: فيديو {edit_style} - {dim}\n#Mediawy_Studio #AI_Context #Shorts")

        except Exception as e: st.error(f"⚠️ خطأ: {str(e)}")
