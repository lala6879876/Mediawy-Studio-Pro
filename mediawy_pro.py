import streamlit as st
import os
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import re

# --- 1. استيراد المحركات الحديثة (MoviePy 2.x) ---
import moviepy as mp
from moviepy.video.VideoClip import ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

# إعداد محرك الصور للسيرفر (Linux)
if os.name == 'posix': 
    os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"
else: 
    os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"

# --- 2. إعداد المجلدات ---
MEDIA_DIR = "Mediawy_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- 3. محركات الرسم والذكاء (ثبات العناصر + النصوص) ---
def create_static_layer(size, logo_path, banner_text, show_banner):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("arial.ttf", size[1] // 25)
    except: font = ImageFont.load_default()
    
    # 8- بنر سفلي اختياري
    if show_banner and banner_text:
        draw.rectangle([0, size[1]-80, size[0], size[1]], fill=(0,0,0,180))
        draw.text((40, size[1]-65), banner_text, font=font, fill="white")
    
    # 9- اللوجو الثابت
    if logo_path:
        logo = Image.open(logo_path).convert("RGBA").resize((size[0]//6, size[0]//6))
        img.paste(logo, (size[0]-size[0]//6-30, 30), logo)
    return ImageClip(np.array(img))

def create_word_clip(size, text, start_t, dur):
    # 7- تأثير الكلمة بكلمة (Clipchamp Style)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("arial.ttf", size[1] // 15)
    except: font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    draw.rectangle([size[0]//2-tw//2-20, size[1]//2-th//2-10, size[0]//2+tw//2+20, size[1]//2+th//2+10], fill=(0,0,0,160))
    draw.text((size[0]//2-tw//2, size[1]//2-th//2), text, font=font, fill="yellow")
    return ImageClip(np.array(img)).with_start(start_t).with_duration(dur).with_position('center')

# --- 4. واجهة المستخدم (الـ 11 إضافة) ---
st.set_page_config(page_title="Mediawy Mega V38", layout="wide")
st.markdown("<h1 style='text-align:center; color:#FF0000;'>🎬 Mediawy Studio <span style='color:#00E5FF;'>V38 Masterpiece</span></h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ مركز التحكم الشامل")
    
    # 1 & 2 & 5: المونتاج والأبعاد
    st.subheader("📺 1. ستايل الفيديو")
    dim = st.selectbox("📏 2- الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    edit_style = st.selectbox("🎭 1- النمط الفني:", ["سينمائي 🎬", "درامي 🎭", "وثائقي 📜"])
    st.divider() # 11- فواصل
    
    # 3: الصوت و ElevenLabs
    st.subheader("🎙️ 3- هندسة الصوت")
    audio_source = st.radio("المصدر:", ["بشري 🎤", "AI (GTTS)", "ElevenLabs 💎"])
    el_key, el_voice = "", ""
    if "ElevenLabs" in audio_source:
        el_key = st.text_input("1. ElevenLabs API Key", type="password")
        el_voice = st.text_input("2. Voice ID", value="pNInz6obpgnu9P6ky9M8")
        st.info("3. المربع الثالث: اكتب النص بالأسفل")
    
    ai_text = st.text_area("✍️ النص (زود الليمت 500 كلمة):", height=150)
    user_audio = st.file_uploader("ارفع ملف الصوت البشري")
    st.divider()

    # 6: الموسيقى الخلفية
    st.subheader("🎵 6- الموسيقى الخلفية")
    bg_music_opt = st.toggle("تفعيل الموسيقى التلقائية", value=True)
    duck_vol = st.slider("مستوى خفض الموسيقى (Ducking):", 0.05, 0.40, 0.10)
    st.divider()

    # 4: الصور
    st.subheader("🖼️ 4- محرك الصور")
    img_mode = st.radio("الجلب:", ["أوتوماتيك (سياق AI)", "يدوي (رفع حتى 500)"])
    user_imgs = st.file_uploader("ارفع صورك (ليمت 500)", accept_multiple_files=True)
    st.divider()

    # 8 & 9: الهوية
    st.subheader("🚩 الهوية والبنر")
    show_banner = st.checkbox("8- تفعيل بنر سفلي متحرك", value=True)
    marquee_text = st.text_input("نص البنر:")
    logo_file = st.file_uploader("9- ارفع اللوجو")

# --- 5. محرك الإنتاج الملياري ---
if st.button("🚀 إطلاق خط الإنتاج الشامل", use_container_width=True):
    if not (ai_text or user_audio) or not logo_file:
        st.error("⚠️ ناقص بيانات (النص واللوجو)!")
    else:
        try:
            status = st.info("⏳ جاري بناء الفيديو بكافة الإضافات والرفاهيات...")
            
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

            # [المشاهد]
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
                
                # 1- زووم ودخلات ناعمة (Ken Burns)
                c = ImageClip(p).with_duration(dur_per_clip).resized(height=h)
                z = 1.25 if i % 2 == 0 else 0.8 # زووم إن وزووم أوت
                c = c.resized(lambda t: 1 + (z-1) * (t/dur_per_clip)).with_crossfadein(0.5)
                
                # نمط المونتاج
                if "درامي" in edit_style:
                    c = c.with_effects([lambda cl: cl.image_transform(lambda im: (im * 0.7).astype('uint8'))])
                
                img_clips.append(c)
                sub_clips.append(create_word_clip((w, h), sentence, i*dur_per_clip, dur_per_clip))

            video_track = concatenate_videoclips(img_clips, method="compose")

            # [9- اللوجو و 8- البنر]
            l_p = os.path.join(ASSETS_DIR, "l.png")
            with open(l_p, "wb") as f: f.write(logo_file.getbuffer())
            static_layer = create_static_layer((w, h), l_p, marquee_text, show_banner).with_duration(total_dur)

            # [6- الموسيقى]
            if bg_music_opt:
                bg = AudioFileClip("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3").with_duration(total_dur).with_volume_scaled(duck_vol)
                final_audio = CompositeAudioClip([voice_clip.with_volume_scaled(1.2), bg])
            else: final_audio = voice_clip

            # [الرندر النهائي]
            final_vid = CompositeVideoClip([video_track, static_layer] + sub_clips, size=(w, h)).with_audio(final_audio)
            out_p = os.path.join(VIDEOS_DIR, "Masterpiece_V38.mp4")
            final_vid.write_videofile(out_p, fps=24, codec="libx264")
            
            st.video(out_p)
            st.success("🔥 مبروك! المكنة طلعت قماش كامل الرفاهية أونلاين!")
            
            # 10- قسم الـ SEO
            st.divider()
            st.subheader("📋 10- اقتراحات النشر (SEO)")
            c1, c2 = st.columns(2)
            with c1:
                st.write("**الاسم والوصف:**")
                st.code(f"أسرار {sentences[0][:30]}...\nشاهد للنهاية لمعرفة التفاصيل!")
            with c2:
                st.write("**الهاشتاجات والكلمات:**")
                st.code(f"#Mediawy_Studio #AI #Shorts #Marketing")

        except Exception as e: st.error(f"⚠️ خطأ: {str(e)}")
