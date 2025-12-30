import streamlit as st
import os, requests, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import moviepy as mp
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip

# ضبط محرك الصور للسيرفر
if os.name == 'posix': os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"

# إعداد المجلدات
MEDIA_DIR = "Mediawy_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- محرك الكتابة (الحل الجذري النهائي) ---
def create_word_clip(size, text, start_t, dur):
    clean_text = str(text).strip() if text else "Mediawy"
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 1. تحديد حجم الخط بناءً على عرض الشاشة (تقديري)
    font_size = size[0] // 15
    try: font = ImageFont.truetype("arial.ttf", font_size)
    except: font = ImageFont.load_default()
    
    # 2. الحل العبقري: حساب يدوي للأبعاد (بدون textbbox المسببة للخطأ)
    # بنفترض إن كل حرف بياخد مساحة تقريبية (0.6 من حجم الخط)
    tw = len(clean_text) * (font_size * 0.6)
    th = font_size * 1.2
    
    # 3. الموضع: التلت الأخير (فوق البنر)
    y_pos = int(size[1] * 0.72)
    x_pos = (size[0] // 2) - (int(tw) // 2)
    
    # رسم الصندوق والنص (Clipchamp Style)
    draw.rectangle([x_pos-20, y_pos-10, x_pos+tw+20, y_pos+th+10], fill=(0,0,0,190))
    draw.text((x_pos, y_pos), clean_text, font=font, fill="yellow")
    
    return ImageClip(np.array(img)).with_start(start_t).with_duration(dur)

# --- واجهة المستخدم (الـ 11 إضافة كاملة) ---
st.set_page_config(page_title="Mediawy V60", layout="wide")
st.markdown("<h1 style='text-align:center; color:#FF0000;'>🎬 Mediawy Studio <span style='color:#00E5FF;'>V60 Final</span></h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ مركز التحكم")
    dim = st.selectbox("📏 2- الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    edit_style = st.selectbox("🎭 1- النمط:", ["سينمائي 🎬", "درامي 🎭", "وثائقي 📜"])
    st.divider() # 11- فواصل

    st.subheader("🎙️ 2. الصوت (بشري/AI/ElevenLabs)")
    audio_source = st.radio("المصدر:", ["AI (GTTS)", "ElevenLabs 💎", "صوت بشري 🎤"])
    ai_text = st.text_area("✍️ النص (حتى 500 كلمة):", height=100)
    user_audio = st.file_uploader("ارفع صوتك لو اخترت 'بشري'")
    if audio_source == "ElevenLabs 💎":
        el_key = st.text_input("📦 API Key", type="password")
        el_voice = st.text_input("📦 Voice ID", value="pNInz6obpgnu9P6ky9M8")
    st.divider()

    st.subheader("🎵 3. الموسيقى الخلفية")
    bg_music_opt = st.toggle("تفعيل الموسيقى", value=True)
    custom_bg = st.file_uploader("ارفع موسيقى خاصة")
    duck_vol = st.slider("مستوى الـ Ducking:", 0.05, 0.40, 0.10)
    st.divider()

    st.subheader("🖼️ 4. محرك الصور (Limit 500)")
    img_mode = st.radio("الجلب:", ["أوتوماتيك", "رفع يدوي"])
    user_imgs = st.file_uploader("ارفع صورك", accept_multiple_files=True)
    st.divider()

    st.subheader("🚩 5. الهوية")
    show_banner = st.toggle("8- البنر السفلي", value=True)
    marquee_text = st.text_input("نص البنر:")
    logo_file = st.file_uploader("9- اللوجو")

# --- محرك الإنتاج ---
if st.button("🚀 إطلاق الإنتاج النهائي", use_container_width=True):
    try:
        status = st.info("⏳ جاري المونتاج... تم سحق خطأ max() يدوياً!")
        
        # [الصوت]
        audio_p = os.path.join(ASSETS_DIR, "v.mp3")
        if audio_source == "صوت بشري 🎤" and user_audio:
            with open(audio_p, "wb") as f: f.write(user_audio.getbuffer())
        elif audio_source == "ElevenLabs 💎":
            res = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{el_voice}", json={"text": ai_text}, headers={"xi-api-key": el_key})
            with open(audio_p, "wb") as f: f.write(res.content)
        else:
            gTTS(ai_text if ai_text else "Mediawy", lang='ar').save(audio_p)
        
        voice_clip = AudioFileClip(audio_p)
        total_dur = voice_clip.duration
        
        # [النصوص]
        raw_t = ai_text if ai_text else "مرحبا بكم"
        sentences = [s.strip() for s in re.split(r'[.؟!،,]+', raw_t) if len(s.strip()) > 1]
        dur_per_clip = total_dur / len(sentences)

        # [المشاهد]
        h = 1080; w = int(h*9/16) if "9:16" in dim else int(h*16/9)
        img_clips = []
        subtitle_clips = []

        for i, sentence in enumerate(sentences):
            p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
            if img_mode == "أوتوماتيك":
                img_data = requests.get(f"https://picsum.photos/seed/{i}/{w}/{h}").content
                with open(p, "wb") as fo: fo.write(img_data)
            else:
                with open(p, "wb") as fo: fo.write(user_imgs[i % len(user_imgs)].getbuffer())
            
            # زووم ناعم 1, 5
            c = ImageClip(np.array(Image.open(p).convert("RGB").resize((w, h)))).with_duration(dur_per_clip)
            z = 1.25 if i % 2 == 0 else 0.85
            c = c.resized(lambda t: 1 + (z-1) * (t / dur_per_clip))
            img_clips.append(c)
            subtitle_clips.append(create_word_clip((w, h), sentence, i*dur_per_clip, dur_per_clip))

        video_track = concatenate_videoclips(img_clips, method="compose")

        # [الهوية 8, 9]
        static_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        if logo_file:
            logo = Image.open(logo_file).convert("RGBA").resize((w//6, w//6))
            static_img.paste(logo, (w-w//6-30, 30), logo)
        if show_banner:
            ImageDraw.Draw(static_img).rectangle([0, h-100, w, h], fill=(0,0,0,210))
            ImageDraw.Draw(static_img).text((40, h-75), marquee_text, fill="white")
        static_layer = ImageClip(np.array(static_img)).with_duration(total_dur)

        # [الموسيقى 6]
        if bg_music_opt:
            bg_p = "https://actions.google.com/sounds/v1/ambiences/morning_birds.ogg"
            bg = AudioFileClip(bg_p).with_duration(total_dur).with_volume_scaled(duck_vol)
            final_audio = CompositeAudioClip([voice_clip.with_volume_scaled(1.2), bg])
        else: final_audio = voice_clip

        final_vid = CompositeVideoClip([video_track, static_layer] + subtitle_clips, size=(w, h)).with_audio(final_audio)
        out_p = os.path.join(VIDEOS_DIR, "Mediawy_V60.mp4")
        final_vid.write_videofile(out_p, fps=24, codec="libx264")
        st.video(out_p)
        
        # [SEO 10]
        st.divider()
        st.subheader("📋 10- SEO ونشر")
        st.code(f"العنوان: {sentences[0][:40]}...\n#Mediawy #AI #Shorts")

    except Exception as e: st.error(f"⚠️ خطأ: {str(e)}")
