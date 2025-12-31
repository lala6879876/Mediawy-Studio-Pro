import streamlit as st
import os, requests, re, io, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip, vfx

# 1- إعداد البيئة (11- فواصل المجلدات والأدوات)
MEDIA_DIR = "Mediawy_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- 4. محرك الصور الحديدي (تعديل جذري لضمان الظهور) ---
def get_verified_image(query, path, size, index):
    w, h = size
    # استخراج كلمات مفتاحية قوية
    keywords = re.findall(r'\w+', query)
    search = keywords[0] if keywords else "nature"
    
    # محاولة من 3 مصادر مختلفة لضمان عدم الفشل
    urls = [
        f"https://loremflickr.com/{w}/{h}/{search}?lock={index}",
        f"https://picsum.photos/seed/{index}/{w}/{h}",
        f"https://placehold.co/{w}x{h}/000000/FFFFFF/png?text={search}" # حل أخير لو النت قطع تماماً
    ]
    
    for url in urls:
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                img = Image.open(io.BytesIO(resp.content)).convert("RGB").resize(size)
                img.save(path, "JPEG")
                # التأكد حرفياً من وجود الملف ومساحته
                if os.path.exists(path) and os.path.getsize(path) > 100:
                    return True
        except:
            continue
    return False

# --- 7. محرك نصوص الترجمة ---
def create_subtitle(size, text, start_t, dur):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    f_size = size[0] // 16
    try: font = ImageFont.truetype("arial.ttf", f_size)
    except: font = ImageFont.load_default()
    tw = len(text) * (f_size * 0.6)
    th = f_size * 1.2
    y_pos, x_pos = int(size[1] * 0.75), (size[0] // 2) - (int(tw) // 2)
    draw.rectangle([x_pos-20, y_pos-10, x_pos+tw+20, y_pos+th+10], fill=(0,0,0,180))
    draw.text((x_pos, y_pos), text, font=font, fill="yellow")
    return ImageClip(np.array(img)).with_start(start_t).with_duration(dur)

# --- واجهة المستخدم (الـ 11 إضافة حرفياً) ---
st.set_page_config(page_title="Mediawy V88", layout="wide")
st.markdown("<h1 style='text-align:center; color:#FF4B4B;'>🎬 Mediawy Studio V88 - Photo Force</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ مركز التحكم")
    dim = st.selectbox("📏 2- الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    st.divider()
    audio_src = st.radio("🎙️ 3- مصدر الصوت:", ["بشري 🎤", "AI 🤖"])
    u_voice = st.file_uploader("ارفع تعليقك الصوتي") if "بشري" in audio_src else None
    ai_text = st.text_area("✍️ النص (اكتب جمل واضحة):", value="العزيمة هي سر النجاح. ميدياوي استوديو معك في كل خطوة.")
    st.divider()
    bg_music_opt = st.toggle("🎵 6- موسيقى خلفية", value=True)
    u_music = st.file_uploader("ارفع الموسيقى")
    st.divider()
    img_mode = st.radio("🖼️ 4- الصور:", ["أوتوماتيك", "رفع يدوي"])
    u_imgs = st.file_uploader("ارفع صورك يدوياً", accept_multiple_files=True)
    logo_file = st.file_uploader("9- اللوجو")

# --- محرك الرندر المطور ---
if st.button("🚀 إطلاق الرندر الملياري المصلح"):
    try:
        status = st.info("⏳ جاري فحص الصور وتطبيق نظام Zoom & Pan...")
        
        # [معالجة الصوت]
        audio_p = os.path.join(ASSETS_DIR, "v.mp3")
        if u_voice:
            with open(audio_p, "wb") as f: f.write(u_voice.getbuffer())
        else:
            gTTS(ai_text, lang='ar').save(audio_p)
        voice = AudioFileClip(audio_p)
        total_dur = voice.duration

        # [بناء المشاهد]
        sentences = [s.strip() for s in re.split(r'[.؟!،]+', ai_text) if len(s.strip()) > 1]
        dur_scene = total_dur / len(sentences)
        h = 1080; w = int(h*9/16) if "9:16" in dim else int(h*16/9)
        
        img_clips = []
        sub_clips = []

        for i, sent in enumerate(sentences):
            p = os.path.join(ASSETS_DIR, f"sc_{i}.jpg")
            # إجبار التحميل
            if img_mode == "أوتوماتيك":
                get_verified_image(sent, p, (w, h), i)
            else:
                with open(p, "wb") as f: f.write(u_imgs[i % len(u_imgs)].getbuffer())
            
            # التأكد من ظهور الصورة (الحل الحاسم)
            if os.path.exists(p):
                c = ImageClip(p).with_duration(dur_scene + 0.4)
                # 1, 5- تأثير الزووم السينمائي
                z_factor = 1.15 if i % 2 == 0 else 0.85
                c = c.resized(lambda t: 1 + (z_factor-1) * (t / dur_scene))
                img_clips.append(c)
                sub_clips.append(create_subtitle((w, h), sent, i*dur_scene, dur_scene))

        video_track = concatenate_videoclips(img_clips, method="compose", padding=-0.4)

        # [الهوية واللوجو]
        overlay_clips = []
        if logo_file:
            logo = Image.open(logo_file).convert("RGBA").resize((w//6, w//6))
            logo_path = os.path.join(ASSETS_DIR, "logo.png")
            logo.save(logo_path)
            overlay_clips.append(ImageClip(logo_path).with_duration(total_dur).with_position(("right", "top")))

        final = CompositeVideoClip([video_track] + overlay_clips + sub_clips, size=(w, h)).with_audio(voice)
        
        out_f = os.path.join(VIDEOS_DIR, "Final_Mediawy_V88.mp4")
        final.write_videofile(out_f, fps=24, codec="libx264")
        st.video(out_f)
        
        # 10- SEO
        st.divider()
        st.code(f"Title: {sentences[0][:40]} #Mediawy #AI #Success")

    except Exception as e:
        st.error(f"⚠️ خطأ: {str(e)}")
