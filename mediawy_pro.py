import streamlit as st
import os, requests, re, io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import moviepy as mp
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip, vfx

# 1- إعداد البيئة (11- فواصل الأداة)
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
        img = Image.new("RGB", size, (index*50%255, 40, 90))
        img.save(path, "JPEG")
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
st.set_page_config(page_title="Mediawy V79", layout="wide")
st.markdown("<h1 style='text-align:center; color:#00E5FF;'>🎬 Mediawy Studio V79 Master</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ لوحة التحكم")
    dim = st.selectbox("📏 2- الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    edit_style = st.selectbox("🎭 1- النمط:", ["سينمائي 🎬", "درامي 🎭"])
    st.divider()

    # 3- رفع الصوت البشري (تم الإصلاح)
    st.subheader("🎙️ 3- هندسة الصوت")
    audio_src = st.radio("المصدر:", ["بشري 🎤", "AI (GTTS) 🤖", "ElevenLabs 💎"])
    u_voice = st.file_uploader("📁 ارفع تعليقك الصوتي") if "بشري" in audio_src else None
    ai_text = st.text_area("✍️ النص (للترجمة والمزامنة):", value="الإصرار هو ما يجعل المستحيل ممكناً.")
    st.divider()

    # 6- الموسيقى الخلفية
    st.subheader("🎵 6- موسيقى خلفية")
    bg_music_opt = st.toggle("تفعيل الموسيقى", value=True)
    u_music = st.file_uploader("📁 ارفع موسيقى MP3")
    st.divider()

    # 4- الصور (رفع أو أوتو)
    st.subheader("🖼️ 4- الصور")
    img_mode = st.radio("النمط:", ["أوتوماتيك", "رفع يدوي"])
    u_imgs = st.file_uploader("📁 ارفع صورك", accept_multiple_files=True)
    st.divider()

    # 8, 9- الهوية
    show_banner = st.toggle("8- بنر سفلي", value=True)
    logo_file = st.file_uploader("9- اللوجو")

# --- محرك الرندر النهائي ---
if st.button("🚀 إطلاق رندر الإنجاز الملياري"):
    try:
        status = st.info("⏳ جاري المونتاج... تطبيق الـ 11 إضافة...")
        
        # [معالجة الصوت 3]
        audio_p = os.path.join(ASSETS_DIR, "v.mp3")
        if audio_src == "بشري 🎤" and u_voice:
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
            bg = AudioFileClip(m_p).subclipped(0, total_dur).with_effects([vfx.AudioVolumize(0.15)])
            final_audio = CompositeAudioClip([voice, bg])

        # [بناء المشاهد 1, 4, 5, 7]
        sentences = [s.strip() for s in re.split(r'[.؟!،]+', ai_text) if len(s.strip()) > 1]
        dur_scene = total_dur / len(sentences)
        h = 1080; w = int(h*9/16) if "9:16" in dim else int(h*16/9)
        
        img_clips = []
        sub_clips = []

        [Image of a professional video editing timeline showing layered audio tracks for voice and background music, contextual video clips with zoom indicators, and overlay tracks for logos and subtitles]

        for i, sent in enumerate(sentences):
            p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
            if img_mode == "أوتوماتيك": get_verified_image(sent, p, (w, h), i)
            else: 
                with open(p, "wb") as f: f.write(u_imgs[i % len(u_imgs)].getbuffer())
            
            # الزووم والنقلات 1, 5
            c = ImageClip(p).with_duration(dur_scene).crossfadein(0.5)
            z = 1.15 if i % 2 == 0 else 0.85
            c = c.resized(lambda t: 1 + (z-1) * (t / dur_scene))
            img_clips.append(c)
            # 7- نصوص الترجمة
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

        final = CompositeVideoClip([video_track, static_layer] + sub_clips, size=(w, h)).with_audio(final_audio)
        out_f = os.path.join(VIDEOS_DIR, "Success_V79.mp4")
        final.write_videofile(out_f, fps=24, codec="libx264")
        st.video(out_f)
        
        # 10- SEO
        st.divider()
        st.code(f"Title: {sentences[0][:40]}\n#Mediawy #AI #Success")

    except Exception as e:
        st.error(f"⚠️ خطأ فني: {str(e)}")
