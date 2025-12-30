import streamlit as st
import os
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import re

# --- 1. الاستدعاء الحديث (حل الأزمة الجذري) ---
import moviepy as mp
# بننادي الأدوات مباشرة من mp لمنع أخطاء المسارات الفرعية
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip

# ضبط محرك الصور أونلاين
if os.name == 'posix': 
    os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"
else: 
    os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"

# --- 2. إعداد المجلدات ---
MEDIA_DIR = "Mediawy_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- 3. محركات الرسم (ثبات الهوية + تأثير Clipchamp) ---
def create_static_layer(size, logo_path, banner_text, show_banner):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("arial.ttf", size[1] // 25)
    except: font = ImageFont.load_default()
    
    if show_banner and banner_text:
        draw.rectangle([0, size[1]-120, size[0], size[1]-20], fill=(0,0,0,180))
        draw.text((40, size[1]-100), banner_text, font=font, fill="white")
    
    if logo_path:
        logo = Image.open(logo_path).convert("RGBA").resize((size[0]//6, size[0]//6))
        img.paste(logo, (size[0]-size[0]//6-30, 30), logo)
    return ImageClip(np.array(img))

def create_word_by_word_clip(size, text, start_t, dur):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("arial.ttf", size[1] // 15)
    except: font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    draw.rectangle([size[0]//2-tw//2-20, size[1]//2-th//2-10, size[0]//2+tw//2+20, size[1]//2+th//2+10], fill=(0,0,0,160))
    draw.text((size[0]//2-tw//2, size[1]//2-th//2), text, font=font, fill="yellow")
    return ImageClip(np.array(img)).with_start(start_t).with_duration(dur).with_position('center')

# --- 4. واجهة المستخدم (الـ 11 إضافة كاملة) ---
st.set_page_config(page_title="Mediawy Mega V41", layout="wide")
st.markdown("<h1 style='text-align:center; color:#FF0000;'>🎬 Mediawy Studio <span style='color:#00E5FF;'>V41 Final</span></h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ مركز التحكم الشامل")
    
    st.subheader("📺 1. ستايل الفيديو")
    dim = st.selectbox("📏 2- الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    edit_style = st.selectbox("🎭 1- النمط الفني:", ["سينمائي 🎬", "درامي 🎭", "وثائقي 📜"])
    st.divider() # 11- فواصل

    st.subheader("🎙️ 2. هندسة الصوت (Limit 500)")
    audio_source = st.radio("المصدر:", ["AI (GTTS)", "ElevenLabs 💎", "بشري 🎤"])
    el_key, el_voice = "", ""
    if "ElevenLabs" in audio_source:
        el_key = st.text_input("📦 1. ElevenLabs API Key", type="password")
        el_voice = st.text_input("📦 2. Voice ID", value="pNInz6obpgnu9P6ky9M8")
        st.info("📦 3. النص: اكتبه في المربع أدناه")
    
    ai_text = st.text_area("✍️ النص (حتى 500 كلمة):", height=150)
    user_audio = st.file_uploader("ارفع ملف الصوت البشري")
    st.divider()

    st.subheader("🎵 3. الموسيقى (اختيارية)")
    bg_music_opt = st.toggle("تفعيل الموسيقى + Ducking", value=True)
    duck_vol = st.slider("مستوى الموسيقى الخلفية:", 0.05, 0.40, 0.10)
    st.divider()

    st.subheader("🖼️ 4. محرك الصور (Limit 500)")
    img_mode = st.radio("الجلب:", ["أوتوماتيك (سياق AI)", "يدوي (رفع حتى 500)"])
    user_imgs = st.file_uploader("ارفع صورك", accept_multiple_files=True)
    st.divider()

    st.subheader("🚩 5. الهوية والبنر")
    show_banner = st.toggle("8- تفعيل البنر السفلي", value=True)
    marquee_text = st.text_input("نص البنر السفلي:")
    logo_file = st.file_uploader("9- ارفع اللوجو")

# --- 5. محرك الإنتاج الملياري ---
if st.button("🚀 إطلاق خط الإنتاج الشامل", use_container_width=True):
    if not (ai_text or user_audio) or not logo_file:
        st.error("⚠️ برجاء إكمال البيانات (النص واللوجو)!")
    else:
        try:
            status = st.info("⏳ جاري المونتاج بأحدث التقنيات...")
            
            # [الصوت]
            audio_p = os.path.join(ASSETS_DIR, "v.mp3")
            if "ElevenLabs" in audio_source:
                res = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{el_voice}", json={"text": ai_text}, headers={"xi-api-key": el_key})
                with open(audio_p, "wb") as f: f.write(res.content)
            elif "AI" in audio_source:
                gTTS(ai_text, lang='ar').save(audio_p)
            else:
                with open(audio_p, "wb") as f: f.write(user_audio.getbuffer())
            
            voice_clip = AudioFileClip(audio_p)
            total_dur = voice_clip.duration

            # [7- تقسيم Clipchamp]
            sentences = [s.strip() for s in re.split(r'[.؟!،,]+', ai_text) if len(s.strip()) > 3]
            dur_per_clip = total_dur / len(sentences) if sentences else total_dur

            # [المشاهد - 1- زووم ودخلات ناعمة]
            h = 1080; w = int(h*9/16) if "9:16" in dim else int(h*16/9)
            img_clips = []
            sub_clips = []

            for i, sentence in enumerate(sentences):
                p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
                if "أوتوماتيك" in img_mode:
                    img_data = requests.get(f"https://images.unsplash.com/photo-1500000000000?w={w}&h={h}&q=80").content
                    with open(p, "wb") as fo: fo.write(img_data)
                else:
                    with open(p, "wb") as fo: fo.write(user_imgs[i % len(user_imgs)].getbuffer())
                
                # زووم ناعم ودخلات (5- التأثيرات)
                c = ImageClip(p).with_duration(dur_per_clip).resized(height=h)
                z_factor = 1.25 if i % 2 == 0 else 0.85 
                c = c.resized(lambda t: 1 + (z_factor - 1) * (t / dur_per_clip)).with_crossfadein(0.5)
                
                img_clips.append(c)
                sub_clips.append(create_word_by_word_clip((w, h), sentence, i*dur_per_clip, dur_per_clip))

            video_track = concatenate_videoclips(img_clips, method="compose")

            # [الهوية واللوجو]
            l_p = os.path.join(ASSETS_DIR, "l.png")
            with open(l_p, "wb") as f: f.write(logo_file.getbuffer())
            static_layer = create_static_layer((w, h), l_p, marquee_text, show_banner).with_duration(total_dur)

            # [6- الموسيقى الخلفية]
            if bg_music_opt:
                bg = AudioFileClip("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3").with_duration(total_dur).with_volume_scaled(duck_vol)
                final_audio = CompositeAudioClip([voice_clip.with_volume_scaled(1.2), bg])
            else: final_audio = voice_clip

            # الرندر النهائي
            final_vid = CompositeVideoClip([video_track, static_layer] + sub_clips, size=(w, h)).with_audio(final
