import streamlit as st
import os
import numpy as np
import re
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import moviepy as mp
from moviepy.video.VideoClip import ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

# --- 1. إعدادات البيئة والمجلدات ---
MEDIA_DIR = "Mediawy_Shorts"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
for d in [ASSETS_DIR]: os.makedirs(d, exist_ok=True)

# --- 2. محرك النصوص والطبقات ---

def create_subtitles_word_by_word(size, text, start_t, duration):
    """إنشاء نصوص تظهر كلمة بكلمة بأسلوب Clipchamp"""
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("arial.ttf", size[1] // 18)
    except: font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    # رسم خلفية نصف شفافة للنص
    draw.rectangle([size[0]//2-tw//2-20, size[1]//2-th//2-10, 
                    size[0]//2+tw//2+20, size[1]//2+th//2+10], fill=(0,0,0,150))
    draw.text((size[0]//2-tw//2, size[1]//2-th//2), text, font=font, fill="yellow")
    return ImageClip(np.array(img)).with_start(start_t).with_duration(duration).with_position('center')

def create_dua_banner(size, duration):
    """إنشاء شريط أدعية متحرك في أسفل الفيديو"""
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("arial.ttf", size[1] // 25)
    except: font = ImageFont.load_default()
    
    # خلفية الشريط الأسفل
    draw.rectangle([0, size[1]-100, size[0], size[1]], fill=(0, 0, 0, 180))
    dua_text = "سبحان الله وبحمده .. سبحان الله العظيم .. استغفر الله واتوب إليه"
    draw.text((50, size[1]-70), dua_text, font=font, fill="white")
    
    # ملاحظة: التحريك الحقيقي يتم عبر تغيير Position في MoviePy
    return ImageClip(np.array(img)).with_duration(duration)

# --- 3. واجهة المستخدم ---
st.title("🎬 مصنع فيديوهات الشورتس (النسخة الإسلامية)")
st.sidebar.header("⚙️ الإعدادات")

with st.sidebar:
    ai_text = st.text_area("✍️ اكتب النص (حتى 500 كلمة):", placeholder="اكتب القصة أو الموضوع هنا...")
    bg_music_url = st.text_input("🔗 رابط موسيقى هادئة (MP3):", "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3")
    ducking = st.slider("🔊 مستوى الموسيقى:", 0.05, 0.30, 0.10)
    user_images = st.file_uploader("🖼️ ارفع صور الفيديو:", accept_multiple_files=True)
    logo = st.file_uploader("🏷️ ارفع اللوجو الخاص بك:")

if st.button("🚀 ابدأ صناعة الفيديو"):
    if not ai_text or not user_images:
        st.error("⚠️ يرجى كتابة النص ورفع الصور!")
    else:
        try:
            with st.spinner("⏳ جاري المونتاج..."):
                # [أ] تحويل النص لصوت
                audio_path = os.path.join(ASSETS_DIR, "voice.mp3")
                gTTS(ai_text, lang='ar').save(audio_path)
                voice_clip = AudioFileClip(audio_path)
                total_duration = voice_clip.duration

                # [ب] تقسيم النص لكلمات (Subtitles)
                words = ai_text.split()
                dur_per_word = total_duration / len(words)
                
                # [ج] إعداد المشاهد (زووم + أبعاد شورتس)
                h, w = 1920, 1080
                clips = []
                for i, img_file in enumerate(user_images):
                    p = os.path.join(ASSETS_DIR, f"img_{i}.jpg")
                    with open(p, "wb") as f: f.write(img_file.getbuffer())
                    
                    # تأثير الزووم الناعم (Ken Burns)
                    img_clip = ImageClip(p).resized(height=h).with_duration(total_duration/len(user_images))
                    img_clip = img_clip.with_effects([lambda c: c.resized(lambda t: 1 + 0.1 * (t / c.duration))])
                    clips.append(img_clip)
                
                main_video = concatenate_videoclips(clips, method="compose")

                # [د] إضافة طبقة الكلمات (Subtitle Layer)
                sub_layers = []
                for i, word in enumerate(words):
                    sub_layers.append(create_subtitles_word_by_word((w, h), word, i*dur_per_word, dur_per_word))

                # [هـ] إضافة شريط الأدعية واللوجو
                banner = create_dua_banner((w, h), total_duration)
                
                # [و] الموسيقى الخلفية
                bg_music = AudioFileClip(bg_music_url).with_duration(total_duration).with_volume_scaled(ducking)
                final_audio = CompositeAudioClip([voice_clip, bg_music])

                # [ز] التجميع النهائي
                final_video = CompositeVideoClip([main_video, banner] + sub_layers, size=(w, h)).with_audio(final_audio)
                
                output_p = "Shorts_Output.mp4"
                final_video.write_videofile(output_p, fps=24, codec="libx264")
                
                st.video(output_p)
                st.success("✅ تم الإنتاج بنجاح!")
                
                # اقتراح SEO
                st.divider()
                st.subheader("📋 بيانات النشر المقترحة:")
                st.code(f"عنوان الفيديو: {words[0]} {words[1]}... #shorts #islamic #foryou")

        except Exception as e:
            st.error(f"❌ حدث خطأ: {e}")
