import streamlit as st
import os
import time
import random
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS

# --- 1. حلول الاستقرار الجذري (تأمين FFmpeg و MoviePy) ---
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except:
    pass

from moviepy.editor import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips

# --- 2. إعداد المجلدات ---
BASE_PATH = os.getcwd()
MEDIA_DIR = os.path.join(BASE_PATH, "Mediawy_Studio")
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- 3. محرك الرسم والفلاتر (Pillow) - لمنع خطأ Primitive ---
def process_frame(img_path, text, logo_path, size, marquee_text, style):
    # فتح الصورة ومعالجتها
    img = Image.open(img_path).convert("RGBA").resize(size)
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # 🎭 تطبيق أنماط المونتاج
    if style == "درامي":
        img = img.point(lambda p: p * 0.6) # تعتيم درامي
    elif style == "سينمائي":
        img = img.point(lambda p: p * 1.3) # ألوان سينمائية زاهية
        
    font_size = size[1] // 15
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # ✨ نصوص Clipchamp (رسم يدوي متزامن)
    if text:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.rectangle([size[0]//2-tw//2-20, size[1]//2-th//2-10, 
                        size[0]//2+tw//2+20, size[1]//2+th//2+10], fill=(0,0,0,180))
        draw.text((size[0]//2-tw//2, size[1]//2-th//2), text, font=font, fill="yellow")

    # 🚩 إضافة اللوجو
    if logo_path:
        logo = Image.open(logo_path).convert("RGBA").resize((size[0]//6, size[0]//6))
        img.paste(logo, (size[0]-size[0]//6-20, 20), logo)

    # 🎞️ البنر السفلي (Marquee)
    if marquee_text:
        draw.rectangle([0, size[1]-60, size[0], size[1]], fill=(0,0,0,255))
        draw.text((20, size[1]-50), marquee_text, font=font, fill="white")

    return np.array(Image.alpha_composite(img, overlay).convert("RGB"))

# --- 4. واجهة المستخدم (فواصل دقيقة للأدوات الـ 11) ---
st.set_page_config(page_title="Mediawy Mega Studio", layout="wide")
st.markdown("<h1 style='text-align:center; color:#e60000;'>Mediawy Studio <span style='color:#00e5ff;'>V11 Ultra</span></h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ مركز التحكم")
    dim = st.selectbox("📏 1. الأبعاد:", ["9:16 (Shorts/TikTok)", "16:9 (YouTube)"])
    edit_style = st.selectbox("🎭 2. نمط المونتاج:", ["سينمائي", "درامي", "وثائقي"])
    st.markdown("---")
    
    audio_source = st.radio("🎤 3. مصدر الصوت:", ["بشري", "AI (GTTS)", "ElevenLabs"])
    el_key = st.text_input("ElevenLabs Key", type="password") if audio_source == "ElevenLabs" else ""
    el_voice = st.text_input("Voice ID", value="pNInz6obpgnu9P6ky9M8") if audio_source == "ElevenLabs" else ""
    ai_text = st.text_area("النص (حتى 500 كلمة):", height=150)
    user_audio = st.file_uploader("ارفع الصوت البشري (لو متاح)")
    st.markdown("---")
    
    st.subheader("🎵 4. الموسيقى ومؤثر الخفض")
    bg_music_opt = st.toggle("تفعيل الموسيقى التلقائية", value=True)
    ducking_strength = st.slider("🔇 خفض الموسيقى عند الكلام (Ducking):", 0.05, 0.4, 0.1)
    st.markdown("---")
    
    img_mode = st.radio("🖼️ 5. الصور:", ["يدوي (بشرى)", "أوتوماتيك AI"])
    user_imgs = st.file_uploader("ارفع حتى 500 صورة", accept_multiple_files=True)
    st.markdown("---")
    
    enable_clipchamp = st.toggle("✨ 6. نصوص Clipchamp", value=True)
    enable_marquee = st.toggle("🎞️ 7. بنر سفلي", value=False)
    marquee_text = st.text_input("نص البنر:", "Mediawy Studio 2025")
    logo_file = st.file_uploader("🚩 8. ارفع اللوجو")

# --- 5. محرك الإنتاج الرئيسي ---
if st.button("إطلاق خط الإنتاج النهائي الشامل 🚀", use_container_width=True):
    if not (ai_text or user_audio) or not logo_file:
        st.error("⚠️ يرجى التأكد من رفع اللوجو وكتابة النص!")
    else:
        status = st.empty()
        try:
            # أ- الصوت
            status.info("🎙️ جاري هندسة الصوت...")
            audio_p = os.path.join(ASSETS_DIR, "final_voice.mp3")
            if audio_source == "ElevenLabs":
                res = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{el_voice}", 
                                    json={"text": ai_text, "model_id": "eleven_multilingual_v2"}, 
                                    headers={"xi-api-key": el_key})
                with open(audio_p, "wb") as f: f.write(res.content)
            elif audio_source == "AI (GTTS)":
                gTTS(ai_text, lang='ar').save(audio_p)
            else:
                with open(audio_p, "wb") as f: f.write(user_audio.getbuffer())
            
            voice_clip = AudioFileClip(audio_p)
            dur = voice_clip.duration

            # ب- الموسيقى مع مؤثر Ducking
            if bg_music_opt:
                bg_data = requests.get("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3").content
                bg_p = os.path.join(ASSETS_DIR, "bg_music.mp3")
                with open(bg_p, "wb") as f: f.write(bg_data)
                # مؤثر التعلية والخفض
                bg_clip = AudioFileClip(bg_p).volumex(ducking_strength).set_duration(dur)
                final_audio = CompositeAudioClip([voice_clip.volumex(1.2), bg_clip])
            else:
                final_audio = voice_clip

            # ج- المونتاج (زووم، فلاتر، نقلات)
            status.info("🎨 جاري المونتاج والرسم السينمائي...")
            h = 1080; w = int(h*9/16) if "9:16" in dim else int(h*16/9)
            l_p = os.path.join(ASSETS_DIR, "logo_main.png")
            with open(l_p, "wb") as f: f.write(logo_file.getbuffer())
            
            img_clips = []
            source_list = user_imgs if img_mode == "يدوي (بشرى)" else [None]*5
            img_dur = dur / len(source_list)
            
            for i, f in enumerate(source_list):
                p = os.path.join(ASSETS_DIR, f"frame_{i}.jpg")
                if f:
                    with open(p, "wb") as fo: fo.write(f.getbuffer())
                else:
                    img_data = requests.get(f"https://picsum.photos/seed/{i}/{w}/{h}").content
                    with open(p, "wb") as fo: fo.write(img_data)
                
                # الرسم المباشر لتفادي خطأ Primitive
                scene_txt = f"Scene {i+1}" if enable_clipchamp else ""
                frame = process_frame(p, scene_txt, l_p, (w, h), marquee_text if enable_marquee else None, edit_style)
                
                c = ImageClip(frame).set_duration(img_dur).crossfadein(0.5)
                # تأثير الزووم (Ken Burns)
                z = 1.15 if i % 2 == 0 else 0.85
                c = c.resize(lambda t: 1 + (z-1) * (t/img_dur))
                img_clips.append(c)
            
            final_vid = concatenate_videoclips(img_clips, method="compose").set_audio(final_audio)
            
            # هـ- الرندر النهائي
            out_p = os.path.join(VIDEOS_DIR, "Mediawy_Final_Master.mp4")
            final_vid.write_videofile(out_p, fps=24, codec="libx264", audio_codec="aac")
            
            st.video(out_p)
            st.success("✅ مبروك يا برنس! المكنة طلعت قماش عالمي.")
            
            # 📋 SEO - بيانات النشر
            st.markdown("---")
            st.subheader("📋 10. بيانات SEO المقترحة")
            st.code(f"الاسم: فيديو {edit_style} بجودة {dim}\n#Mediawy_Studio #AI #Moneatage")
            
        except Exception as e:
            st.error(f"⚠️ خطأ: {str(e)}")