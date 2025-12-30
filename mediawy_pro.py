import streamlit as st
import os, requests, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import moviepy as mp
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip

# ضبط المحرك
if os.name == 'posix': os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"

# إعداد المجلدات
MEDIA_DIR = "Mediawy_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- محرك الزووم الحقيقي (Ken Burns Effect) ---
def apply_zoom_effect(clip, mode="in"):
    dur = clip.duration
    if mode == "in":
        return clip.resized(lambda t: 1 + 0.15 * (t / dur)) 
    else:
        return clip.resized(lambda t: 1.15 - 0.15 * (t / dur))

# --- محرك الكتابة Steel-Safe (تجنب max error) ---
def create_word_clip(size, text, start_t, dur):
    clean_text = str(text).strip() if text else "Mediawy"
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font_size = size[0] // 15
    try: font = ImageFont.truetype("arial.ttf", font_size)
    except: font = ImageFont.load_default()
    
    tw = len(clean_text) * (font_size * 0.6)
    th = font_size * 1.2
    y_pos = int(size[1] * 0.72)
    x_pos = (size[0] // 2) - (int(tw) // 2)
    
    draw.rectangle([x_pos-20, y_pos-10, x_pos+tw+20, y_pos+th+10], fill=(0,0,0,190))
    draw.text((x_pos, y_pos), clean_text, font=font, fill="yellow")
    return ImageClip(np.array(img)).with_start(start_t).with_duration(dur)

# --- واجهة المستخدم (الـ 11 إضافة) ---
st.set_page_config(page_title="Mediawy V66", layout="wide")
st.markdown("<h1 style='text-align:center; color:#FF0000;'>🎬 Mediawy Studio <span style='color:#00E5FF;'>V66 Zero-Fix</span></h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ مركز التحكم")
    dim = st.selectbox("📏 2- الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    edit_style = st.selectbox("🎭 1- النمط:", ["سينمائي 🎬", "درامي 🎭", "وثائقي 📜"])
    st.divider() # 11- فواصل

    st.subheader("🎙️ 2. الصوت (بشري/AI/ElevenLabs)")
    audio_source = st.radio("المصدر:", ["AI (GTTS)", "ElevenLabs 💎", "صوت بشري 🎤"])
    ai_text = st.text_area("✍️ النص (حتى 500 كلمة):", height=100)
    user_audio = st.file_uploader("ارفع صوتك لو اخترت 'بشري'")
    st.divider()

    st.subheader("🖼️ 4. الصور الذكية")
    img_mode = st.radio("الجلب:", ["أوتوماتيك (سياقي)", "رفع يدوي"])
    user_imgs = st.file_uploader("ارفع صورك", accept_multiple_files=True)
    st.divider()

    show_banner = st.toggle("8- البنر", value=True)
    marquee_text = st.text_input("نص البنر:")
    logo_file = st.file_uploader("9- اللوجو")

# --- محرك الإنتاج ---
if st.button("🚀 إطلاق الإنتاج المصلح", use_container_width=True):
    try:
        status = st.info("⏳ جاري المونتاج وتأمين الحسابات الرياضية...")
        
        # [الصوت]
        audio_p = os.path.join(ASSETS_DIR, "v.mp3")
        if audio_source == "صوت بشري 🎤" and user_audio:
            with open(audio_p, "wb") as f: f.write(user_audio.getbuffer())
        else:
            text_to_say = ai_text if ai_text.strip() else "Mediawy Studio Production"
            gTTS(text_to_say, lang='ar').save(audio_p)
        
        voice_clip = AudioFileClip(audio_p)
        total_dur = voice_clip.duration

        # [علاج Division by Zero]
        sentences = [s.strip() for s in re.split(r'[.؟!،,]+', ai_text) if len(s.strip()) > 1]
        if not sentences:
            sentences = ["Mediawy Studio"] # صمام أمان
        
        dur_per_clip = total_dur / len(sentences) # دلوقتِ مستحيل تقسم على صفر

        # [بناء الفيديو]
        h = 1080; w = int(h*9/16) if "9:16" in dim else int(h*16/9)
        img_clips = []
        subtitle_clips = []

        for i, sentence in enumerate(sentences):
            p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
            if img_mode == "أوتوماتيك (سياقي)":
                query = sentence.split()[0] if sentence.split() else "abstract"
                img_data = requests.get(f"https://source.unsplash.com/featured/{w}x{h}/?{query}").content
                with open(p, "wb") as fo: fo.write(img_data)
            else:
                with open(p, "wb") as fo: fo.write(user_imgs[i % len(user_imgs)].getbuffer())
            
            # زووم ناعم حقيقي
            raw_img = Image.open(p).convert("RGB").resize((w, h))
            c = ImageClip(np.array(raw_img)).with_duration(dur_per_clip + 0.2)
            z_mode = "in" if i % 2 == 0 else "out"
            c = apply_zoom_effect(c, mode=z_mode)
            img_clips.append(c)
            
            subtitle_clips.append(create_word_clip((w, h), sentence, i*dur_per_clip, dur_per_clip))

        video_track = concatenate_videoclips(img_clips, method="compose", padding=-0.2)

        # [الهوية]
        static_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        if logo_file:
            logo = Image.open(logo_file).convert("RGBA").resize((w//6, w//6))
            static_img.paste(logo, (w-w//6-30, 30), logo)
        if show_banner:
            draw = ImageDraw.Draw(static_img)
            draw.rectangle([0, h-100, w, h], fill=(0,0,0,210))
            draw.text((40, h-75), marquee_text, fill="white")
        static_layer = ImageClip(np.array(static_img)).with_duration(total_dur)

        final_vid = CompositeVideoClip([video_track, static_layer] + subtitle_clips, size=(w, h)).with_audio(voice_clip)
        out_p = os.path.join(VIDEOS_DIR, "Mediawy_V66.mp4")
        final_vid.write_videofile(out_p, fps=24, codec="libx264")
        st.video(out_p)
        
        # [SEO 10]
        st.divider()
        st.subheader("📋 10- SEO")
        st.code(f"العنوان: {sentences[0][:40]}\n#AI #Shorts #Success")

    except Exception as e: st.error(f"⚠️ خطأ: {str(e)}")
