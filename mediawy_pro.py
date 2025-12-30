import streamlit as st
import os, requests, re, io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import moviepy as mp
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip

# ضبط المحرك
if os.name == 'posix': os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"

# المجلدات
MEDIA_DIR = "Mediawy_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- دالة التحقق من سلامة الصورة (حل مشكلة identify) ---
def download_safe_image(query, path, size):
    w, h = size
    urls = [
        f"https://source.unsplash.com/featured/{w}x{h}/?{query}",
        f"https://picsum.photos/{w}/{h}"
    ]
    for url in urls:
        try:
            resp = requests.get(url, timeout=10)
            img = Image.open(io.BytesIO(resp.content))
            img.verify() # التأكد من سلامة الملف
            img = Image.open(io.BytesIO(resp.content)).convert("RGB").resize(size)
            img.save(path, "JPEG")
            return True
        except:
            continue
    return False

# --- محرك الزووم الحقيقي (Ken Burns) ---
def apply_zoom_effect(clip, mode="in"):
    dur = clip.duration
    if mode == "in":
        return clip.resized(lambda t: 1 + 0.18 * (t / dur))
    else:
        return clip.resized(lambda t: 1.18 - 0.18 * (t / dur))

# --- محرك الكتابة (Clipchamp Style) ---
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

# --- واجهة المستخدم (الـ 11 إضافة كاملة) ---
st.set_page_config(page_title="Mediawy V68", layout="wide")
st.markdown("<h1 style='text-align:center; color:#FF0000;'>🎬 Mediawy Studio <span style='color:#00E5FF;'>V68 Shield</span></h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ مركز التحكم الملياري")
    dim = st.selectbox("📏 الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    edit_style = st.selectbox("🎭 النمط:", ["سينمائي 🎬", "درامي 🎭", "وثائقي 📜"])
    st.divider() # 11- فواصل

    st.subheader("🎙️ الصوت")
    audio_source = st.radio("المصدر:", ["AI (GTTS)", "ElevenLabs 💎", "صوت بشري 🎤"])
    ai_text = st.text_area("✍️ النص (حتى 500 كلمة):", value="الإرادة القوية تكسر كل الصعاب.")
    user_audio = st.file_uploader("ارفع صوتك لو اخترت 'بشري'")
    st.divider()

    st.subheader("🖼️ الصور")
    img_mode = st.radio("الجلب:", ["أوتوماتيك (سياقي)", "رفع يدوي"])
    user_imgs = st.file_uploader("ارفع صورك", accept_multiple_files=True)
    st.divider()

    show_banner = st.toggle("8- البنر السفلي", value=True)
    marquee_text = st.text_input("نص البنر:")
    logo_file = st.file_uploader("9- اللوجو")

# --- محرك الإنتاج ---
if st.button("🚀 إطلاق رندر الإنجاز", use_container_width=True):
    try:
        status = st.info("⏳ جاري فحص سلامة الصور وتطبيق الزووم السينمائي...")
        
        # [1. تأمين الصوت]
        text_content = ai_text.strip() if ai_text.strip() else "Mediawy Studio"
        audio_p = os.path.join(ASSETS_DIR, "v.mp3")
        if audio_source == "صوت بشري 🎤" and user_audio:
            with open(audio_p, "wb") as f: f.write(user_audio.getbuffer())
        else:
            gTTS(text_content, lang='ar').save(audio_p)
        
        voice_clip = AudioFileClip(audio_p)
        total_dur = voice_clip.duration
        sentences = [s.strip() for s in re.split(r'[.؟!،,]+', text_content) if len(s.strip()) > 1]
        if not sentences: sentences = ["Mediawy"]
        dur_per_clip = total_dur / len(sentences)

        # [2. بناء المشاهد بالزووم المطور]
        h = 1080; w = int(h*9/16) if "9:16" in dim else int(h*16/9)
        img_clips = []
        subtitle_clips = []

        for i, sentence in enumerate(sentences):
            p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
            if img_mode == "أوتوماتيك (سياقي)":
                query = sentence.split()[0] if sentence.split() else "vision"
                success = download_safe_image(query, p, (w, h))
                if not success: continue
            else:
                with open(p, "wb") as fo: fo.write(user_imgs[i % len(user_imgs)].getbuffer())
            
            # زووم سينمائي حقيقي Ken Burns
            c = ImageClip(p).with_duration(dur_per_clip + 0.5)
            z_mode = "in" if i % 2 == 0 else "out"
            c = apply_zoom_effect(c, mode=z_mode).with_crossfadein(0.5)
            img_clips.append(c)
            
            subtitle_clips.append(create_word_clip((w, h), sentence, i*dur_per_clip, dur_per_clip))

        video_track = concatenate_videoclips(img_clips, method="compose", padding=-0.5)

        # [3. الهوية]
        static_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        if logo_file:
            logo = Image.open(logo_file).convert("RGBA").resize((w//6, w//6))
            static_img.paste(logo, (w-w//6-30, 30), logo)
        if show_banner:
            ImageDraw.Draw(static_img).rectangle([0, h-100, w, h], fill=(0,0,0,210))
            ImageDraw.Draw(static_img).text((40, h-75), marquee_text, fill="white")
        static_layer = ImageClip(np.array(static_img)).with_duration(total_dur)

        final_vid = CompositeVideoClip([video_track, static_layer] + subtitle_clips, size=(w, h)).with_audio(voice_clip)
        out_p = os.path.join(VIDEOS_DIR, "Final_Mediawy_V68.mp4")
        final_vid.write_videofile(out_p, fps=24, codec="libx264")
        st.video(out_p)
        
        # [10. SEO]
        st.code(f"SEO: {sentences[0]} #AI #Shorts")

    except Exception as e: st.error(f"⚠️ خطأ: {str(e)}")
