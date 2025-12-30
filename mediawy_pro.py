import streamlit as st
import os, requests, re, io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import moviepy as mp
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip

# ضبط محرك الصور للسيرفر
if os.name == 'posix': os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"

# المجلدات
MEDIA_DIR = "Mediawy_Studio"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- محرك البحث عن صور ذكية (4- الصور أوتوماتيك حسب كل جملة) ---
def get_verified_image(query, path, size):
    w, h = size
    # تنظيف الكلمة للبحث (أول كلمتين من الجملة)
    search_query = "+".join(query.split()[:2])
    url = f"https://picsum.photos/seed/{search_query}/{w}/{h}" # استخدام seed يضمن تنوع الصور
    try:
        response = requests.get(url, timeout=10)
        img = Image.open(io.BytesIO(response.content)).convert("RGB").resize(size)
        img.save(path, "JPEG")
        return True
    except:
        # خلفية طوارئ ملونة لو فشل النت
        Image.new("RGB", size, (i*20 % 255, 50, 100)).save(path, "JPEG")
        return True

# --- محرك الزووم والتحريك (1, 5) ---
def apply_pro_zoom(clip, index):
    dur = clip.duration
    # تبادل بين زووم للداخل وللخارج لإضافة حيوية
    if index % 2 == 0:
        return clip.resized(lambda t: 1 + 0.2 * (t / dur))
    else:
        return clip.resized(lambda t: 1.2 - 0.2 * (t / dur))

# --- واجهة المستخدم (الـ 11 إضافة كاملة) ---
st.set_page_config(page_title="Mediawy V72", layout="wide")
st.markdown("<h1 style='text-align:center; color:#FF0000;'>🎬 Mediawy Studio <span style='color:#00E5FF;'>V72 Multi-Scene</span></h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ مركز التحكم")
    dim = st.selectbox("📏 2- الأبعاد:", ["9:16 (Shorts)", "16:9 (YouTube)"])
    edit_style = st.selectbox("🎭 1- النمط:", ["سينمائي 🎬", "درامي 🎭", "وثائقي 📜"])
    st.divider()

    st.subheader("🎙️ 2. الصوت")
    audio_source = st.radio("المصدر:", ["AI (GTTS)", "ElevenLabs 💎", "بشري 🎤"])
    ai_text = st.text_area("✍️ النص (اكتب جمل تفصل بينها نقطة):", value="النجاح يبدأ بخطوة. العمل الجاد يحقق الأحلام. ميدياوي استوديو هو رفيقك.")
    user_audio = st.file_uploader("ارفع ملف الصوت")
    st.divider()

    st.subheader("🖼️ 4. الصور")
    img_mode = st.radio("الجلب:", ["أوتوماتيك (سياقي متغير)", "رفع يدوي"])
    user_imgs = st.file_uploader("ارفع صورك (ارفع أكتر من صورة)", accept_multiple_files=True)
    st.divider()

    show_banner = st.toggle("8- البنر", value=True)
    marquee_text = st.text_input("نص البنر:")
    logo_file = st.file_uploader("9- اللوجو")

# --- محرك الرندر الملياري ---
if st.button("🚀 إطلاق رندر المشاهد المتعددة", use_container_width=True):
    try:
        status = st.info("⏳ جاري تحليل الجمل وتوليد صور لكل مشهد...")
        
        # [الصوت]
        audio_p = os.path.join(ASSETS_DIR, "voice.mp3")
        if audio_source == "بشري 🎤" and user_audio:
            with open(audio_p, "wb") as f: f.write(user_audio.getbuffer())
        else:
            gTTS(ai_text if ai_text else "Mediawy", lang='ar').save(audio_p)
        
        voice_clip = AudioFileClip(audio_p)
        total_dur = voice_clip.duration
        
        # تقسيم النص لجمل حقيقية لضمان تعدد الصور
        sentences = [s.strip() for s in re.split(r'[.؟!]+', ai_text) if len(s.strip()) > 2]
        if not sentences: sentences = ["تأكد من وضع نقطة بين الجمل", "ليتمكن المحرك من تغيير الصور"]
        
        dur_per_clip = total_dur / len(sentences)

        # [بناء المشاهد المتعددة]
        h = 1080; w = int(h*9/16) if "9:16" in dim else int(h*16/9)
        img_clips = []
        
        

        for i, sentence in enumerate(sentences):
            p = os.path.join(ASSETS_DIR, f"scene_{i}.jpg")
            if img_mode == "أوتوماتيك (سياقي متغير)":
                get_verified_image(sentence, p, (w, h))
            elif user_imgs:
                # لو رفعت صور يدوي، بياخدهم بالترتيب
                with open(p, "wb") as fo: fo.write(user_imgs[i % len(user_imgs)].getbuffer())
            
            # زووم ناعم وتغيير مشهد
            c = ImageClip(p).with_duration(dur_per_clip)
            c = apply_pro_zoom(c, i)
            img_clips.append(c)

        # دمج المشاهد (تغيير الصورة أوتوماتيك مع كل جملة)
        video_track = concatenate_videoclips(img_clips, method="compose")

        # [الهوية واللوجو]
        static_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        if logo_file:
            logo = Image.open(logo_file).convert("RGBA").resize((w//6, w//6))
            static_img.paste(logo, (w-w//6-30, 30), logo)
        static_layer = ImageClip(np.array(static_img)).with_duration(total_dur)

        final_vid = CompositeVideoClip([video_track, static_layer], size=(w, h)).with_audio(voice_clip)
        out_p = os.path.join(VIDEOS_DIR, "Mediawy_MultiScene_V72.mp4")
        final_vid.write_videofile(out_p, fps=24, codec="libx264")
        st.video(out_p)
        
        # [10. SEO]
        st.divider()
        st.subheader("📋 10- SEO ونشر")
        st.code(f"العنوان: {sentences[0]} #Mediawy #AI #Video")

    except Exception as e: st.error(f"⚠️ خطأ فني: {str(e)}")
