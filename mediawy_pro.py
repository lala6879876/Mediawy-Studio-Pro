import streamlit as st
import os
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import re

# --- 1. الاستدعاءات الاحترافية (MoviePy 2.x Modern) ---
import moviepy as mp
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip

if os.name == 'posix': 
    os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"

# --- 2. إعداد المجلدات ---
MEDIA_DIR = "Mediawy_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- 3. محرك الصور الذكي (صمام الأمان ضد الصور التالفة) ---
def get_safe_image(path, size):
    try:
        with Image.open(path) as img:
            img.verify() 
        img = Image.open(path).convert("RGB").resize(size)
        return np.array(img)
    except:
        dummy = Image.new("RGB", size, (20, 20, 20)) # خلفية داكنة كبديل
        return np.array(dummy)

# --- 4. محرك الكتابة (7- Clipchamp Style في الثلث الأخير) ---
def create_word_clip(size, text, start_t, dur):
    if not text.strip(): text = "..."
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("arial.ttf", size[1] // 18)
    except: font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    
    # التمركز في الثلث الأخير (المكان الاحترافي فوق البنر)
    y_pos = int(size[1] * 0.75) - (th // 2)
    x_pos = (size[0] // 2) - (tw // 2)
    
    # خلفية النص لضمان القراءة
    draw.rectangle([x_pos-20, y_pos-10, x_pos+tw+20, y_pos+th+10], fill=(0,0,0,180))
    draw.text((x_pos, y_pos), text, font=font, fill="yellow")
    return ImageClip(np.array(img)).with_start(start_t).with_duration(dur)

# --- 5. واجهة المستخدم (الـ 11 إضافة كاملة) ---
st.set_page_config(page_title="Mediawy V51", layout="wide")
st.markdown("<h1 style='text-align:center; color:#FF0000;'>🎬 Mediawy Studio <span style='color:#00E5FF;'>V51 Ultimate</span></h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ مركز التحكم")
    
    # 1, 2, 5: المونتاج والأبعاد
    st.subheader("📺 1. نمط الفيديو")
    dim = st.selectbox("📏 2- الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    edit_style = st.selectbox("🎭 1- النمط:", ["سينمائي 🎬", "درامي 🎭", "وثائقي 📜"])
    st.divider() # 11- فواصل

    # 3: الصوت و ElevenLabs بـ 3 مربعات
    st.subheader("🎙️ 2. هندسة الصوت (Limit 500)")
    audio_source = st.radio("المصدر:", ["AI (GTTS)", "ElevenLabs 💎", "بشري 🎤"])
    el_key, el_voice = "", ""
    if "ElevenLabs" in audio_source:
        el_key = st.text_input("📦 1. ElevenLabs API Key", type="password")
        el_voice = st.text_input("📦 2. Voice ID", value="pNInz6obpgnu9P6ky9M8")
        st.info("📦 3. النص: اكتبه في المربع أدناه")
    
    ai_text = st.text_area("✍️ النص (حتى 500 كلمة):", height=150)
    user_audio = st.file_uploader("ارفع صوتك البشري")
    st.divider()

    # 6: الموسيقى
    st.subheader("🎵 3. الموسيقى")
    bg_music_opt = st.toggle("تفعيل الموسيقى التلقائية", value=True)
    duck_vol = st.slider("مستوى Ducking:", 0.05, 0.40, 0.10)
    st.divider()

    # 4: الصور
    st.subheader("🖼️ 4. محرك الصور (Limit 500)")
    img_mode = st.radio("الجلب:", ["أوتوماتيك (AI)", "يدوي (رفع)"])
    user_imgs = st.file_uploader("ارفع صورك", accept_multiple_files=True)
    st.divider()

    # 8, 9: البنر واللوجو
    st.subheader("🚩 5. الهوية والبنر")
    show_banner = st.toggle("8- تفعيل البنر السفلي", value=True)
    marquee_text = st.text_input("نص البنر (متحرك):")
    logo_file = st.file_uploader("9- ارفع اللوجو")

# --- 6. محرك الرندر الملياري ---
if st.button("🚀 إطلاق خط الإنتاج المصلح", use_container_width=True):
    if not (ai_text or user_audio) or not logo_file:
        st.error("⚠️ يرجى إكمال البيانات (النص واللوجو)!")
    else:
        try:
            status = st.info("⏳ جاري المونتاج... زووم إن/أوت... مزامنة النصوص...")
            
            # [معالجة الصوت]
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
            sentences = [s.strip() for s in re.split(r'[.؟!،,]+', ai_text) if len(s.strip()) > 2]
            dur_per_clip = total_dur / len(sentences) if sentences else total_dur

            # [المشاهد]
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
                
                # 1, 5: زووم وتأثيرات (Ken Burns)
                z = 1.25 if i % 2 == 0 else 0.85
                c = c.resized(lambda t: 1 + (z-1) * (t / dur_per_clip))
                img_clips.append(c)
                
                # 7: نصوص متزامنة (كلمة بكلمة)
                sub_clips.append(create_word_clip((w, h), sentence, i*dur_per_clip, dur_per_clip))

            # النقلات الناعمة (Padding سلبي لعمل Crossfade)
            video_track = concatenate_videoclips(img_clips, method="compose", padding=-0.3)

            # [8, 9] الهوية والبنر
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

            # [6] الموسيقى
            if bg_music_opt:
                bg = AudioFileClip("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3").with_duration(total_dur).with_volume_scaled(duck_vol)
                final_audio = CompositeAudioClip([voice_clip.with_volume_scaled(1.2), bg])
            else: final_audio = voice_clip

            # الدمج النهائي
            final_vid = CompositeVideoClip([video_track, static_layer] + sub_clips, size=(w, h)).with_audio(final_audio)
            out_p = os.path.join(VIDEOS_DIR, "Mediawy_Final_Pro.mp4")
            final_vid.write_videofile(out_p, fps=24, codec="libx264")
            
            st.video(out_p)
            st.success("🔥 المكنة طلعت قماش بالـ 11 إضافة!")
            
            # 10: SEO واقتراحات النشر
            st.divider()
            st.subheader("📋 10- SEO ونشر")
            st.code(f"العنوان: {sentences[0][:40]}...\n#Mediawy #Shorts #AI_Video")

        except Exception as e: st.error(f"⚠️ خطأ فني: {str(e)}")
