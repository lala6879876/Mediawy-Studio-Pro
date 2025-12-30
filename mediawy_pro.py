import streamlit as st
import os, requests, re, io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import moviepy as mp
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip, vfx

# 1- إعداد البيئة والمجلدات (11- فواصل الأداة)
if os.name == 'posix': os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"
MEDIA_DIR = "Mediawy_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- 4. محرك الصور السياقي (أوتوماتيك) ---
def get_verified_image(query, path, size, index):
    w, h = size
    clean_q = "+".join(re.findall(r'\w+', query)[:2])
    url = f"https://source.unsplash.com/featured/{w}x{h}/?{clean_q},{index}"
    try:
        resp = requests.get(url, timeout=10)
        img = Image.open(io.BytesIO(resp.content)).convert("RGB").resize(size)
        img.save(path, "JPEG")
        return True
    except:
        Image.new("RGB", size, (index*40%255, 60, 100)).save(path, "JPEG")
        return True

# --- 7. محرك نصوص Clipchamp (كلمة بكلمة) ---
def create_subtitle(size, text, start_t, dur):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    f_size = size[0] // 16
    try: font = ImageFont.truetype("arial.ttf", f_size)
    except: font = ImageFont.load_default()
    tw = len(text) * (f_size * 0.65)
    th = f_size * 1.3
    y_pos, x_pos = int(size[1] * 0.72), (size[0] // 2) - (int(tw) // 2)
    draw.rectangle([x_pos-20, y_pos-10, x_pos+tw+20, y_pos+th+10], fill=(0,0,0,190))
    draw.text((x_pos, y_pos), text, font=font, fill="yellow")
    return ImageClip(np.array(img)).with_start(start_t).with_duration(dur)

# --- واجهة المستخدم (تثبيت الـ 11 إضافة) ---
st.set_page_config(page_title="Mediawy V77", layout="wide")
st.markdown("<h1 style='text-align:center; color:#00E5FF;'>🎬 Mediawy Studio V77 Master</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ لوحة التحكم")
    # 2- الأبعاد
    dim = st.selectbox("📏 2- الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    # 1- النمط
    edit_style = st.selectbox("🎭 1- النمط (سينمائي/درامي):", ["سينمائي 🎬", "درامي 🎭", "وثائقي 📜"])
    st.divider()

    # 3- الصوت (بشري/AI/ElevenLabs)
    st.subheader("🎙️ 3- هندسة الصوت (Limit 500)")
    audio_src = st.radio("المصدر:", ["بشري 🎤", "AI (GTTS) 🤖", "ElevenLabs 💎"])
    u_voice = st.file_uploader("📁 ارفع ملف صوتك (3- بشري)") if "بشري" in audio_src else None
    ai_text = st.text_area("✍️ النص (للتعليق والترجمة):", value="النجاح هو القدرة على الذهاب من فشل إلى فشل دون فقدان الحماس.")
    st.divider()

    # 6- الموسيقى (اختيارية)
    st.subheader("🎵 6- الموسيقى الخلفية")
    bg_music_opt = st.toggle("تفعيل الموسيقى", value=True)
    u_music = st.file_uploader("📁 ارفع موسيقى (6- اختيارية)")
    st.divider()

    # 4- الصور
    st.subheader("🖼️ 4- الصور (أوتو/رفع)")
    img_mode = st.radio("النمط:", ["أوتوماتيك (سياقي)", "رفع يدوي (حتى 500)"])
    u_imgs = st.file_uploader("📁 ارفع صورك", accept_multiple_files=True)
    st.divider()

    # 8, 9- الهوية (اللوجو والبنر)
    show_banner = st.toggle("8- بنر سفلي متحرك", value=True)
    logo_file = st.file_uploader("9- اللوجو (9)")

# --- محرك الرندر النهائي (التأثيرات والنقلات 5) ---
if st.button("🚀 إطلاق رندر الإنجاز (V77)"):
    try:
        status = st.info("⏳ جاري معالجة الـ 11 إضافة... استعد للقماش!")
        
        # [الصوت]
        audio_p = os.path.join(ASSETS_DIR, "v.mp3")
        if u_voice:
            with open(audio_p, "wb") as f: f.write(u_voice.getbuffer())
        else:
            gTTS(ai_text, lang='ar').save(audio_p)
        voice = AudioFileClip(audio_p)
        total_dur = voice.duration

        # [الموسيقى 6]
        final_audio = voice
        if bg_music_opt and u_music:
            m_p = os.path.join(ASSETS_DIR, "m.mp3")
            with open(m_p, "wb") as f: f.write(u_music.getbuffer())
            bg = AudioFileClip(m_p).with_duration(total_dur).with_effects([vfx.AudioVolumize(0.15)])
            final_audio = CompositeAudioClip([voice, bg])

        # [بناء المشاهد والزووم 1, 5]
        sentences = [s.strip() for s in re.split(r'[.؟!،]+', ai_text) if len(s.strip()) > 1]
        dur_scene = total_dur / len(sentences)
        h = 1080; w = int(h*9/16) if "9:16" in dim else int(h*16/9)
        
        img_clips = []
        sub_clips = []

        for i, sent in enumerate(sentences):
            p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
            if img_mode == "أوتوماتيك": get_verified_image(sent, p, (w, h), i)
            else: 
                with open(p, "wb") as f: f.write(u_imgs[i % len(u_imgs)].getbuffer())
            
            # التأثيرات والنقلات 5 والزووم 1
            c = ImageClip(p).with_duration(dur_scene).crossfadein(0.5)
            # تأثير Ken Burns (زووم سينمائي ناعم)
            z = 1.15 if i % 2 == 0 else 0.85
            c = c.resized(lambda t: 1 + (z-1) * (t / dur_scene))
            img_clips.append(c)
            # 7- نصوص Clipchamp
            sub_clips.append(create_subtitle((w, h), sent, i*dur_scene, dur_scene))

        video_track = concatenate_videoclips(img_clips, method="compose")

        # [8, 9- الهوية]
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        if logo_file:
            logo = Image.open(logo_file).convert("RGBA").resize((w//6, w//6))
            overlay.paste(logo, (w-w//6-30, 30), logo)
        if show_banner:
            draw = ImageDraw.Draw(overlay)
            draw.rectangle([0, h-100, w, h], fill=(0,0,0,210))
            draw.text((40, h-75), "Mediawy Studio - Powered by AI", fill="white")
        static_layer = ImageClip(np.array(overlay)).with_duration(total_dur)

        # الدمج النهائي (رندر شامل)
        final = CompositeVideoClip([video_track, static_layer] + sub_clips, size=(w, h)).with_audio(final_audio)
        out_f = os.path.join(VIDEOS_DIR, "Mediawy_Success_V77.mp4")
        final.write_videofile(out_f, fps=24, codec="libx264")
        st.video(out_f)
        
        # 10- SEO (اسم، وصف، هاشتاج)
        st.divider()
        st.subheader("📋 10- قسم الـ SEO")
        st.code(f"العنوان المقترح: {sentences[0][:40]}\nالوصف: فيديو احترافي تم إنتاجه بواسطة Mediawy Studio.\nالهاشتاجات: #Mediawy #AI #Shorts")

    except Exception as e:
        st.error(f"⚠️ خطأ فني: {str(e)}")
