import streamlit as st
import os, requests, re, io, time, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip, vfx

# 1- إعداد البيئة (11- فواصل المجلدات)
MEDIA_DIR = "Mediawy_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- 4. محرك الصور الحديدي (3 مصادر + فحص الحجم) ---
def get_guaranteed_image(sentence, path, size, index):
    w, h = size
    words = [w for w in re.findall(r'\w+', sentence) if len(w) > 2]
    q = words[0] if words else "vision"
    sources = [
        f"https://loremflickr.com/g/{w}/{h}/{q}?lock={random.randint(1,1000)}",
        f"https://picsum.photos/seed/{random.randint(1,1000)}/{w}/{h}",
        f"https://source.unsplash.com/featured/{w}x{h}/?{q},cinema"
    ]
    for url in sources:
        try:
            resp = requests.get(url, timeout=12)
            if resp.status_code == 200:
                img = Image.open(io.BytesIO(resp.content)).convert("RGB").resize(size)
                img.save(path, "JPEG")
                if os.path.exists(path) and os.path.getsize(path) > 2000: return True
        except: continue
    # Fallback (صورة طوارئ فخمة)
    img = Image.new("RGB", size, (20, 20, 40))
    ImageDraw.Draw(img).rectangle([40, 40, w-40, h-40], outline="white", width=2)
    img.save(path, "JPEG")
    return True

# --- 7. محرك نصوص Clipchamp (الترجمة المفقودة) ---
def create_subtitle(size, text, start_t, dur):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    f_size = size[0] // 16
    try: font = ImageFont.truetype("arial.ttf", f_size)
    except: font = ImageFont.load_default()
    tw = len(text) * (f_size * 0.65)
    th = f_size * 1.3
    y_pos, x_pos = int(size[1] * 0.72), (size[0] // 2) - (int(tw) // 2)
    draw.rectangle([x_pos-20, y_pos-10, x_pos+tw+20, y_pos+th+10], fill=(0,0,0,200))
    draw.text((x_pos, y_pos), text, font=font, fill="yellow")
    return ImageClip(np.array(img)).with_start(start_t).with_duration(dur)

# --- واجهة المستخدم (تثبيت الـ 11 إضافة حرفياً) ---
st.set_page_config(page_title="Mediawy V97 Final", layout="wide")
st.markdown("<h1 style='text-align:center; color:#00E5FF;'>🎬 Mediawy Studio V97 Master</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ لوحة التحكم الشاملة")
    dim = st.selectbox("📏 2- الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    edit_style = st.selectbox("🎭 1- النمط:", ["سينمائي 🎬", "درامي 🎭"])
    st.divider()
    # 3- الصوت
    audio_src = st.radio("🎙️ 3- الصوت:", ["بشري 🎤", "AI 🤖"])
    u_voice = st.file_uploader("ارفع تعليقك الصوتي (MP3/WAV)")
    ai_text = st.text_area("✍️ النص (للترجمة):", value="النجاح ليس صدفة، بل هو عمل شاق وإصرار.")
    st.divider()
    # 6- الموسيقى
    u_music = st.file_uploader("🎵 6- موسيقى خلفية")
    st.divider()
    # 8, 9- الهوية
    show_banner = st.toggle("8- بنر سفلي احترافي", value=True)
    logo_file = st.file_uploader("9- اللوجو الشخصي")

# --- محرك الرندر (تجميع الـ 11 إضافة) ---
if st.button("🚀 إطلاق الرندر الشامل (V97)"):
    try:
        status = st.info("⏳ جاري جرد الـ 11 إضافة... المونتاج يبدأ الآن!")
        
        # [معالجة الصوت]
        audio_p = os.path.join(ASSETS_DIR, "v97_v.mp3")
        if u_voice:
            with open(audio_p, "wb") as f: f.write(u_voice.getbuffer())
        else:
            gTTS(ai_text, lang='ar').save(audio_p)
        voice = AudioFileClip(audio_p)

        # [معالجة الموسيقى 6]
        final_audio = voice
        if u_music:
            m_p = os.path.join(ASSETS_DIR, "v97_m.mp3")
            with open(m_p, "wb") as f: f.write(u_music.getbuffer())
            bg = AudioFileClip(m_p).subclipped(0, voice.duration).with_effects([vfx.AudioVolumize(0.12)])
            final_audio = CompositeAudioClip([voice, bg])

        # [بناء المشاهد والزووم والترجمة 1, 4, 5, 7]
        sentences = [s.strip() for s in re.split(r'[.؟!،]+', ai_text) if len(s.strip()) > 1]
        dur_scene = voice.duration / len(sentences)
        h = 1080; w = int(h*9/16) if "9:16" in dim else int(h*16/9)
        
        img_clips = []
        sub_clips = []

        for i, sent in enumerate(sentences):
            p = os.path.join(ASSETS_DIR, f"v97_i_{i}.jpg")
            get_guaranteed_image(sent, p, (w, h), i)
            
            if os.path.exists(p):
                c = ImageClip(p).with_duration(dur_scene + 0.4)
                # 1, 5- زووم سينمائي
                z = 1.15 if i % 2 == 0 else 0.85
                c = c.resized(lambda t: 1 + (z-1) * (t / dur_scene))
                img_clips.append(c)
                # 7- الترجمة
                sub_clips.append(create_subtitle((w, h), sent, i*dur_scene, dur_scene))

        video_track = concatenate_videoclips(img_clips, method="compose", padding=-0.4)

        # [8, 9- الهوية: بنر ولوجو]
        overlay_elements = []
        # البنر 8
        if show_banner:
            banner_img = Image.new("RGBA", (w, 100), (0, 0, 0, 180))
            ImageDraw.Draw(banner_img).text((40, 35), "Mediawy Studio - Premium Production", fill="white")
            banner_p = os.path.join(ASSETS_DIR, "banner.png")
            banner_img.save(banner_p)
            overlay_elements.append(ImageClip(banner_p).with_duration(voice.duration).with_position(("center", "bottom")))
        # اللوجو 9
        if logo_file:
            logo_p = os.path.join(ASSETS_DIR, "logo_v97.png")
            Image.open(logo_file).convert("RGBA").resize((w//6, w//6)).save(logo_p)
            overlay_elements.append(ImageClip(logo_p).with_duration(voice.duration).with_position(("right", "top")))

        # الدمج النهائي
        final = CompositeVideoClip([video_track] + overlay_elements + sub_clips, size=(w, h)).with_audio(final_audio)
        out_f = os.path.join(VIDEOS_DIR, "Mediawy_V97_Full.mp4")
        final.write_videofile(out_f, fps=24, codec="libx264")
        st.video(out_f)
        
        # 10- SEO
        st.divider()
        st.code(f"Title: {sentences[0][:40]} #Mediawy #AI #Shorts")

    except Exception as e:
        st.error(f"⚠️ خطأ: {str(e)}")
