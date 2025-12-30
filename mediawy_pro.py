import streamlit as st
import os
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import re

# --- 1. استيراد المحركات (Modern MoviePy 2.x) ---
from moviepy.video.VideoClip import ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

# إعداد محرك الصور للسيرفر
if os.name == 'posix': os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"
else: os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"

# --- 2. إنشاء بيئة العمل ---
MEDIA_DIR = "Mediawy_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- 3. دوال التصميم (ثبات العناصر) ---
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

# --- 4. واجهة المستخدم (البيت الكبير) ---
st.set_page_config(page_title="Mediawy Mega V35", layout="wide")
st.markdown("<h1 style='text-align:center; color:#FF0000;'>🎬 Mediawy Studio <span style='color:#00E5FF;'>V35 Ultimate</span></h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🛠️ إعدادات المونتاج")
    dim = st.selectbox("📏 اختيار الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    edit_style = st.selectbox("🎭 النمط الفني:", ["سينمائي 🎬", "درامي 🎭", "وثائقي 📜"])
    
    st.divider()
    st.markdown("### 🎙️ هندسة الصوت (ElevenLabs)")
    audio_source = st.radio("مصدر التعليق:", ["ElevenLabs (احترافي)", "AI (GTTS - مجاني)", "رفع ملف صوتي"])
    el_key = st.text_input("ElevenLabs API Key", type="password") if "ElevenLabs" in audio_source else ""
    el_voice = st.text_input("Voice ID", value="pNInz6obpgnu9P6ky9M8") if "ElevenLabs" in audio_source else ""
    
    ai_text = st.text_area("✍️ النص (حتى 500 كلمة):", height=150)
    user_audio = st.file_uploader("ارفع صوتك المسجل") if "رفع" in audio_source else None

    st.divider()
    st.markdown("### 🎵 الموسيقى و Ducking")
    bg_music_opt = st.toggle("تفعيل الموسيقى التلقائية", value=True)
    duck_vol = st.slider("مستوى خفض الموسيقى وقت الكلام:", 0.05, 0.40, 0.10)

    st.divider()
    st.markdown("### 🖼️ محرك الصور السياقي")
    img_mode = st.radio("طريقة جلب الصور:", ["سياق AI ذكي", "رفع يدوي (حتى 500 صورة)"])
    user_imgs = st.file_uploader("ارفع صورك", accept_multiple_files=True)
    
    st.divider()
    st.markdown("### 🚩 الهوية والبنر")
    marquee_text = st.text_input("نص البنر السفلي:", "Mediawy Studio 2026")
    logo_file = st.file_uploader("ارفع شعارك (Logo)")

# --- 5. محرك الإنتاج العملاق ---
if st.button("🚀 إطلاق خط الإنتاج الملياري", use_container_width=True):
    if not (ai_text or user_audio) or not logo_file:
        st.error("⚠️ برجاء رفع اللوجو وكتابة النص أولاً!")
    else:
        try:
            status = st.info("⏳ جاري تجهيز عتاد الفيديو...")
            
            # [1] معالجة الصوت
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

            # [2] مزامنة النصوص (Clipchamp)
            sentences = [s.strip() for s in re.split(r'[.؟!،,]+', ai_text) if len(s.strip()) > 3]
            num_clips = len(sentences)
            dur_per_clip = total_dur / num_clips if num_clips > 0 else total_dur

            # [3] بناء المشاهد (زووم + فلاتر)
            h = 1080; w = int(h*9/16) if "9:16" in dim else int(h*16/9)
            img_clips = []
            sub_clips = []

            for i, sentence in enumerate(sentences):
                p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
                if "AI" in img_mode:
                    img_data = requests.get(f"https://images.unsplash.com/photo-1500000000000?w={w}&h={h}&q=80").content
                    with open(p, "wb") as fo: fo.write(img_data)
                else:
                    with open(p, "wb") as fo: fo.write(user_imgs[i % len(user_imgs)].getbuffer())
                
                # حركة الزووم السينمائي
                c = ImageClip(p).with_duration(dur_per_clip).resized(height=h)
                z = 1.2 if i % 2 == 0 else 0.8
                c = c.resized(lambda t: 1 + (z-1) * (t/dur_per_clip))
                
                # فلاتر النمط الفني
                if "درامي" in edit_style:
                    c = c.with_effects([lambda cl: cl.image_transform(lambda im: (im * 0.7).astype('uint8'))])
                
                img_clips.append(c)
                sub_clips.append(create_text_clip((w, h), sentence, i*dur_per_clip, dur_per_clip))

            video_track = concatenate_videoclips(img_clips, method="compose")

            # [4] الهوية والبنر (ثابتين فوق الكل)
            l_p = os.path.join(ASSETS_DIR, "l.png")
            with open(l_p, "wb") as f: f.write(logo_file.getbuffer())
            static_layer = create_static_layer((w, h), l_p, marquee_text).with_duration(total_dur)

            # [5] هندسة الصوت النهائية (Ducking)
            if bg_music_opt:
                bg = AudioFileClip("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3").with_duration(total_dur).with_volume_scaled(duck_vol)
                final_audio = CompositeAudioClip([voice_clip.with_volume_scaled(1.2), bg])
            else: final_audio = voice_clip

            # [6] الرندر النهائي
            final_vid = CompositeVideoClip([video_track, static_layer] + sub_clips, size=(w, h)).with_audio(final_audio)
            out_p = os.path.join(VIDEOS_DIR, "Mediawy_Ultimate_V35.mp4")
            final_vid.write_videofile(out_p, fps=24, codec="libx264")
            
            st.video(out_p)
            st.success("🔥 تم إنتاج الفيديو بكل الإضافات والرفاهيات!")
            
            # [7] قسم SEO
            st.divider()
            st.markdown("### 📋 بيانات SEO لزيادة المشاهدات")
            c1, c2 = st.columns(2)
            with c1: st.code(f"العنوان: أسرار {sentences[0][:30]}... | نمط {edit_style}")
            with c2: st.code(f"#Mediawy_Studio #AI_Content #Shorts #Marketing")

        except Exception as e:
            st.error(f"⚠️ خطأ فني: {str(e)}")
