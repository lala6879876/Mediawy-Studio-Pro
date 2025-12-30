import streamlit as st
import os, requests, re, io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import moviepy as mp
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip

# ضبط محرك الصور للسيرفر
if os.name == 'posix': os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"

# المجلدات
MEDIA_DIR = "Mediawy_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- محرك الصور (تجنب identify error) ---
def get_verified_image(query, path, size):
    w, h = size
    sources = [
        f"https://source.unsplash.com/featured/{w}x{h}/?{query}",
        f"https://picsum.photos/{w}/{h}"
    ]
    for url in sources:
        try:
            response = requests.get(url, timeout=10)
            img = Image.open(io.BytesIO(response.content))
            img.verify() 
            img = Image.open(io.BytesIO(response.content)).convert("RGB").resize(size)
            img.save(path, "JPEG")
            return True
        except: continue
    Image.new("RGB", size, (30, 30, 30)).save(path, "JPEG")
    return True

# --- محرك الزووم والنقلات (MoviePy 2.x Compatibility) ---
def apply_pro_zoom(clip, index):
    dur = clip.duration
    # تطبيق الزووم (Ken Burns)
    if index % 2 == 0:
        c = clip.resized(lambda t: 1 + 0.15 * (t / dur))
    else:
        c = clip.resized(lambda t: 1.15 - 0.15 * (t / dur))
    # النقلات الناعمة (التحديث الجديد للأسماء)
    return c.crossfadein(0.5)

# --- محرك الكتابة (Clipchamp Style) ---
def create_subtitle(size, text, start_t, dur):
    clean_text = str(text).strip() if text else "..."
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font_size = size[0] // 16
    try: font = ImageFont.truetype("arial.ttf", font_size)
    except: font = ImageFont.load_default()
    tw = len(clean_text) * (font_size * 0.65)
    th = font_size * 1.3
    y_pos = int(size[1] * 0.75)
    x_pos = (size[0] // 2) - (int(tw) // 2)
    draw.rectangle([x_pos-20, y_pos-10, x_pos+tw+20, y_pos+th+10], fill=(0,0,0,180))
    draw.text((x_pos, y_pos), clean_text, font=font, fill="yellow")
    return ImageClip(np.array(img)).with_start(start_t).with_duration(dur)

# --- واجهة المستخدم (الـ 11 إضافة) ---
st.set_page_config(page_title="Mediawy V70", layout="wide")
st.markdown("<h1 style='text-align:center; color:#FF0000;'>🎬 Mediawy Studio <span style='color:#00E5FF;'>V70 Master</span></h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ مركز التحكم")
    dim = st.selectbox("📏 2- الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    edit_style = st.selectbox("🎭 1- النمط:", ["سينمائي 🎬", "درامي 🎭", "وثائقي 📜"])
    st.divider() # 11- فواصل

    st.subheader("🎙️ 2. الصوت (Limit 500)")
    audio_source = st.radio("المصدر:", ["AI (GTTS)", "ElevenLabs 💎", "صوت بشري 🎤"])
    ai_text = st.text_area("✍️ النص:", value="الإبداع هو أن ترى ما لا يراه الآخرون.")
    user_audio = st.file_uploader("ارفع ملف الصوت")
    st.divider()

    st.subheader("🖼️ 4. الصور")
    img_mode = st.radio("الجلب:", ["أوتوماتيك (سياقي)", "رفع يدوي"])
    user_imgs = st.file_uploader("ارفع صورك", accept_multiple_files=True)
    st.divider()

    show_banner = st.toggle("8- البنر", value=True)
    marquee_text = st.text_input("نص البنر:")
    logo_file = st.file_uploader("9- اللوجو")

# --- محرك الرندر ---
if st.button("🚀 إطلاق رندر الإنجاز المصلح", use_container_width=True):
    try:
        status = st.info("⏳ جاري المونتاج بنظام V70 المستقر...")
        
        # [الصوت]
        audio_p = os.path.join(ASSETS_DIR, "voice.mp3")
        if audio_source == "صوت بشري 🎤" and user_audio:
            with open(audio_p, "wb") as f: f.write(user_audio.getbuffer())
        else:
            gTTS(ai_text if ai_text else "Mediawy", lang='ar').save(audio_p)
        
        voice_clip = AudioFileClip(audio_p)
        total_dur = voice_clip.duration
        sentences = [s.strip() for s in re.split(r'[.؟!،,]+', ai_text) if len(s.strip()) > 1]
        if not sentences: sentences = ["Mediawy Studio Final"]
        dur_per_clip = total_dur / len(sentences)

        # [بناء المشاهد]
        h = 1080; w = int(h*9/16) if "9:16" in dim else int(h*16/9)
        img_clips = []
        sub_clips = []

        for i, sentence in enumerate(sentences):
            p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
            if img_mode == "أوتوماتيك (سياقي)":
                query = sentence.split()[0] if sentence.split() else "art"
                get_verified_image(query, p, (w, h))
            else:
                with open(p, "wb") as fo: fo.write(user_imgs[i % len(user_imgs)].getbuffer())
            
            # زووم ناعم ونقلات (تم تصحيح اسم الدالة)
            c = ImageClip(p).with_duration(dur_per_clip + 0.5)
            c = apply_pro_zoom(c, i)
            img_clips.append(c)
            sub_clips.append(create_subtitle((w, h), sentence, i*dur_per_clip, dur_per_clip))

        video_track = concatenate_videoclips(img_clips, method="compose", padding=-0.5)

        # [الهوية والبنر]
        static_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        if logo_file:
            logo = Image.open(logo_file).convert("RGBA").resize((w//6, w//6))
            static_img.paste(logo, (w-w//6-30, 30), logo)
        if show_banner:
            draw = ImageDraw.Draw(static_img)
            draw.rectangle([0, h-100, w, h], fill=(0,0,0,210))
            draw.text((40, h-75), marquee_text, fill="white")
        static_layer = ImageClip(np.array(static_img)).with_duration(total_dur)

        final_vid = CompositeVideoClip([video_track, static_layer] + sub_clips, size=(w, h)).with_audio(voice_clip)
        out_p = os.path.join(VIDEOS_DIR, "Mediawy_V70_Fixed.mp4")
        final_vid.write_videofile(out_p, fps=24, codec="libx264")
        st.video(out_p)
        
        # [10. SEO]
        st.divider()
        st.subheader("📋 10- SEO")
        st.code(f"العنوان: {sentences[0]} #Mediawy #AI")

    except Exception as e: st.error(f"⚠️ خطأ فني: {str(e)}")
