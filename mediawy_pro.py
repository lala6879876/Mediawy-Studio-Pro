import streamlit as st
import os, requests, re, io, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import moviepy as mp
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip

# ضبط المحرك
if os.name == 'posix': os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"

# المجلدات
MEDIA_DIR = "Mediawy_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- محرك استخراج الكلمات المفتاحية (لضمان صور مرتبطة بالموضوع) ---
def get_keywords(text):
    # تنظيف النص من الكلمات الشائعة اللي بتبوظ البحث
    stop_words = ["من", "في", "على", "إلى", "عن", "مع", "هو", "هي", "كان", "ان"]
    words = re.findall(r'\w+', text)
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    return keywords if keywords else ["video", "cinematic", "digital"]

# --- محرك الصور السياقي المطور (4) ---
def get_contextual_image(sentence, path, size, index):
    w, h = size
    keys = get_keywords(sentence)
    query = keys[0] if keys else "nature"
    # استخدام محرك Unsplash المباشر مع الكلمة المستخرجة + index لضمان التنوع
    url = f"https://source.unsplash.com/featured/{w}x{h}/?{query},{index}"
    try:
        resp = requests.get(url, timeout=12)
        img = Image.open(io.BytesIO(resp.content)).convert("RGB").resize(size)
        img.save(path, "JPEG")
        return True
    except:
        # بديل Picsum بـ Seed متغير
        requests.get(f"https://picsum.photos/seed/{index}/{w}/{h}").content
        return True

# --- محرك الزووم والنقلات (1, 5) ---
def apply_ken_burns(clip, index):
    dur = clip.duration
    if index % 2 == 0:
        return clip.resized(lambda t: 1 + 0.20 * (t / dur))
    else:
        return clip.resized(lambda t: 1.20 - 0.20 * (t / dur))

# --- محرك الكتابة Clipchamp (7) ---
def create_subtitle(size, text, start_t, dur):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    f_size = size[0] // 16
    try: font = ImageFont.truetype("arial.ttf", f_size)
    except: font = ImageFont.load_default()
    tw = len(text) * (f_size * 0.65)
    th = f_size * 1.3
    y_pos, x_pos = int(size[1] * 0.75), (size[0] // 2) - (int(tw) // 2)
    draw.rectangle([x_pos-20, y_pos-10, x_pos+tw+20, y_pos+th+10], fill=(0,0,0,180))
    draw.text((x_pos, y_pos), text, font=font, fill="yellow")
    return ImageClip(np.array(img)).with_start(start_t).with_duration(dur)

# --- واجهة المستخدم (الـ 11 إضافة) ---
st.set_page_config(page_title="Mediawy V73", layout="wide")
st.markdown("<h1 style='text-align:center; color:#FF0000;'>🎬 Mediawy Studio <span style='color:#00E5FF;'>V73 Contextual</span></h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ مركز التحكم")
    dim = st.selectbox("📏 2- الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    edit_style = st.selectbox("🎭 1- النمط:", ["سينمائي 🎬", "درامي 🎭", "وثائقي 📜"])
    st.divider()

    st.subheader("🎙️ 2. الصوت (3)")
    audio_source = st.radio("المصدر:", ["AI (GTTS)", "ElevenLabs 💎", "بشري 🎤"])
    ai_text = st.text_area("✍️ النص:", value="الذكاء الاصطناعي يغير العالم. التكنولوجيا هي مستقبل البشرية. ابدأ رحلتك الآن مع ميدياوي.")
    st.divider()

    st.subheader("🖼️ 4. الصور (بناءً على المحتوى)")
    img_mode = st.radio("النمط:", ["تحليل سياقي أوتوماتيك", "رفع يدوي"])
    user_imgs = st.file_uploader("ارفع صورك", accept_multiple_files=True)
    st.divider()

    show_banner = st.toggle("8- البنر", value=True)
    marquee_text = st.text_input("نص البنر:")
    logo_file = st.file_uploader("9- اللوجو")

# --- محرك الرندر ---
if st.button("🚀 إطلاق رندر الذكاء السياقي", use_container_width=True):
    try:
        status = st.info("⏳ جاري استخراج الكلمات المفتاحية وتحميل الصور المناسبة...")
        
        # [الصوت]
        audio_p = os.path.join(ASSETS_DIR, "v.mp3")
        gTTS(ai_text if ai_text else "Mediawy", lang='ar').save(audio_p)
        voice = AudioFileClip(audio_p)
        total_dur = voice.duration
        
        # تقسيم ذكي للجمل (نقطة، فاصلة، علامة استفهام)
        sentences = [s.strip() for s in re.split(r'[.؟!،,]+', ai_text) if len(s.strip()) > 3]
        if not sentences: sentences = ["تأكد من كتابة نص طويل", "للحصول على مشاهد متنوعة"]
        
        dur_per_scene = total_dur / len(sentences)
        h = 1080; w = int(h*9/16) if "9:16" in dim else int(h*16/9)
        
        img_clips = []
        sub_clips = []

        # 

        for i, sent in enumerate(sentences):
            p = os.path.join(ASSETS_DIR, f"scene_{i}.jpg")
            # تحليل كل جملة لوحدها لجلب صورة معبرة (Contextual)
            get_contextual_image(sent, p, (w, h), i)
            
            # زووم ناعم (Ken Burns)
            c = ImageClip(p).with_duration(dur_per_scene).crossfadein(0.5)
            c = apply_ken_burns(c, i)
            img_clips.append(c)
            
            # نصوص Clipchamp
            sub_clips.append(create_subtitle((w, h), sent, i*dur_per_scene, dur_per_scene))

        # دمج المشاهد
        video_track = concatenate_videoclips(img_clips, method="compose")

        # الهوية
        static_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        if logo_file:
            logo = Image.open(logo_file).convert("RGBA").resize((w//6, w//6))
            static_img.paste(logo, (w-w//6-30, 30), logo)
        static_layer = ImageClip(np.array(static_img)).with_duration(total_dur)

        final_vid = CompositeVideoClip([video_track, static_layer] + sub_clips, size=(w, h)).with_audio(voice)
        out_p = os.path.join(VIDEOS_DIR, "Mediawy_Context_V73.mp4")
        final_vid.write_videofile(out_p, fps=24, codec="libx264")
        st.video(out_p)
        
        # SEO
        st.divider()
        st.subheader("📋 10- SEO")
        st.code(f"العنوان: {sentences[0]} #Mediawy #AI")

    except Exception as e: st.error(f"⚠️ خطأ: {str(e)}")
