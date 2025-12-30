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

# --- 3. محرك الصور الذكي ---
def get_safe_image(path, size):
    try:
        with Image.open(path) as img:
            img.verify() 
        img = Image.open(path).convert("RGB").resize(size)
        return np.array(img)
    except:
        return np.array(Image.new("RGB", size, (20, 20, 20)))

# --- 4. محرك الكتابة (حل نهائي ومطلق لخطأ max) ---
def create_word_clip(size, text, start_t, dur):
    clean_text = str(text).strip() if text else "..."
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    try: font = ImageFont.truetype("arial.ttf", size[1] // 18)
    except: font = ImageFont.load_default()
    
    # 
    # محاولة حساب الأبعاد بأمان تام
    try:
        bbox = draw.textbbox((0, 0), clean_text, font=font)
        if bbox and len(bbox) >= 4:
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
        else: raise ValueError
    except:
        # قيم طوارئ في حال فشل الحساب (منع خطأ max)
        tw, th = size[0] // 2, size[1] // 15

    # ضبط المكان في الثلث الأخير فوق البنر
    y_pos = int(size[1] * 0.72) 
    x_pos = (size[0] // 2) - (tw // 2)
    
    # رسم الصندوق والنص
    draw.rectangle([x_pos-20, y_pos-10, x_pos+tw+20, y_pos+th+10], fill=(0,0,0,180))
    draw.text((x_pos, y_pos), clean_text, font=font, fill="yellow")
    
    return ImageClip(np.array(img)).with_start(start_t).with_duration(dur)

# --- 5. واجهة المستخدم (الـ 11 إضافة كاملة بالفواصل) ---
st.set_page_config(page_title="Mediawy V55", layout="wide")
st.markdown("<h1 style='text-align:center; color:#FF0000;'>🎬 Mediawy Studio <span style='color:#00E5FF;'>V55 Steel</span></h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ مركز التحكم الشامل")
    
    # 1, 2, 5: المونتاج والأبعاد
    st.subheader("📺 1. ستايل الفيديو")
    dim = st.selectbox("📏 2- الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    edit_style = st.selectbox("🎭 1- النمط:", ["سينمائي 🎬", "درامي 🎭", "وثائقي 📜"])
    st.divider() # 11- فواصل

    # 3: الصوت بـ 3 مربعات
    st.subheader("🎙️ 2. هندسة الصوت (Limit 500)")
    audio_source = st.radio("المصدر:", ["AI (GTTS)", "ElevenLabs 💎", "بشري 🎤"])
    el_key, el_voice = "", ""
    if "ElevenLabs" in audio_source:
        el_key = st.text_input("📦 1. API Key", type="password")
        el_voice = st.text_input("📦 2. Voice ID", value="pNInz6obpgnu9P6ky9M8")
        st.info("📦 3. النص: اكتبه في المربع أدناه")
    
    ai_text = st.text_area("✍️ النص (حتى 500 كلمة):", height=150)
    user_audio = st.file_uploader("ارفع ملف الصوت البشري")
    st.divider()

    # 6: الموسيقى
    st.subheader("🎵 3. الموسيقى الخلفية")
    bg_music_opt = st.toggle("تفعيل الموسيقى التلقائية", value=True)
    custom_bg = st.file_uploader("ارفع موسيقى خاصة")
    duck_vol = st.slider("مستوى Ducking:", 0.05, 0.40, 0.10)
    st.divider()

    # 4: الصور
    st.subheader("🖼️ 4. محرك الصور (Limit 500)")
    img_mode = st.radio("الجلب:", ["أوتوماتيك (AI)", "يدوي (رفع)"])
    user_imgs = st.file_uploader("ارفع صورك", accept_multiple_files=True)
    st.divider()

    # 8, 9: الهوية والبنر
    st.subheader("🚩 5. الهوية والبنر")
    show_banner = st.toggle("8- تفعيل البنر السفلي", value=True)
    marquee_text = st.text_input("نص البنر:")
    logo_file = st.file_uploader("9- ارفع اللوجو")

# --- 6. محرك الإنتاج ---
if st.button("🚀 إطلاق خط الإنتاج الفولاذي", use_container_width=True):
    if not (ai_text or user_audio) or not logo_file:
        st.error("⚠️ يرجى إكمال البيانات الأساسية!")
    else:
        try:
            status = st.info("⏳ جاري المونتاج... تم سحق خطأ max() بنظام Steel-Safe...")
            
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
            sentences = [s.strip() for s in re.split(r'[.؟!،,]+', ai_text) if len(s.strip()) > 1]
            if not sentences: sentences = ["Mediawy Studio"]
            dur_per_clip = total_dur / len(sentences)

            h = 1080; w = int(h*9/16) if "9:16" in dim else int(h*16/9)
            img_clips = []
            sub_clips = []

            for i, sentence in enumerate(sentences):
                p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
                if "أوتوماتيك" in img_mode:
                    img_data = requests.get(f"https://picsum.photos/seed/{i}/{w}/{h}").content
                    with open(p, "wb") as fo: fo.write(img_data)
                elif user_imgs:
                    with open(p, "wb") as fo: fo.write(user_imgs[i % len(user_imgs)].getbuffer())
                
                img_array = get_safe_image(p, (w, h))
                c = ImageClip(img_array).with_duration(dur_per_clip)
                z = 1.25 if i % 2 == 0 else 0.85
                c = c.resized(lambda t: 1 + (z-1) * (t / dur_per_clip))
                img_clips.append(c)
                sub_clips.append(create_word_clip((w, h), sentence, i*dur_per_clip, dur_per_clip))

            video_track = concatenate_videoclips(img_clips, method="compose", padding=-0.3)

            # اللوجو والبنر
            l_p = os.path.join(ASSETS_DIR, "l.png")
            with open(l_p, "wb") as f: f.write(logo_file.getbuffer())
            
            static_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            if show_banner:
                ImageDraw.Draw(static_img).rectangle([0, h-100, w, h], fill=(0,0,0,200))
                try: f_banner = ImageFont.truetype("arial.ttf", h//25)
                except: f_banner = ImageFont.load_default()
                ImageDraw.Draw(static_img).text((40, h-75), marquee_text, font=f_banner, fill="white")
            
            logo_img = Image.open(l_p).convert("RGBA").resize((w//6, w//6))
            static_img.paste(logo_img, (w-w//6-30, 30), logo_img)
            static_layer = ImageClip(np.array(static_img)).with_duration(total_dur)

            # الموسيقى
            if bg_music_opt:
                if custom_bg:
                    music_p = os.path.join(ASSETS_DIR, "bg.mp3")
                    with open(music_p, "wb") as f: f.write(custom_bg.getbuffer())
                    bg = AudioFileClip(music_p).with_duration(total_dur).with_volume_scaled(duck_vol)
                else:
                    bg = AudioFileClip("https://actions.google.com/sounds/v1/ambiences/morning_birds.ogg").with_duration(total_dur).with_volume_scaled(duck_vol)
                final_audio = CompositeAudioClip([voice_clip.with_volume_scaled(1.2), bg])
            else: final_audio = voice_clip

            final_vid = CompositeVideoClip([video_track, static_layer] + sub_clips, size=(w, h)).with_audio(final_audio)
            out_p = os.path.join(VIDEOS_DIR, "Mediawy_V55.mp4")
            final_vid.write_videofile(out_p, fps=24, codec="libx264")
            
            st.video(out_p)
            st.success("🔥 مبروك! المكنة اشتغلت بنظام الفلترة الفولاذي.")
            
            # 10- SEO
            st.divider()
            st.subheader("📋 10- SEO")
            st.code(f"العنوان: {sentences[0][:40]}...\n#Mediawy #Shorts #AI")

        except Exception as e: st.error(f"⚠️ خطأ فني: {str(e)}")
