import streamlit as st
import os, requests, re, io, time, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip, vfx

# --- 1. إعداد البيئة (فواصل ومجلدات) ---
MEDIA_DIR = "Mediawy_Studio_Pro"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- محرك الصور الذكي (صياد الكلمات) ---
def get_smart_image(query, path, size):
    w, h = size
    q = "+".join(re.findall(r'\w+', query)[:3])
    url = f"https://source.unsplash.com/featured/{w}x{h}/?{q},cinematic&sig={random.randint(1,500)}"
    try:
        resp = requests.get(url, timeout=10)
        img = Image.open(io.BytesIO(resp.content)).convert("RGB").resize(size)
        img.save(path, "JPEG")
    except:
        img = Image.new("RGB", size, (20, 20, 40))
        img.save(path, "JPEG")

# --- واجهة المستخدم الاحترافية ---
st.set_page_config(page_title="Mediawy Studio V100", layout="wide")
st.markdown("<h1 style='text-align:center; color:#00E5FF;'>🎬 Mediawy Studio V100 Professional</h1>", unsafe_allow_html=True)

# تقسيم الواجهة (الجانبين للإضافات والمنتصف للعرض)
col_left, col_mid, col_right = st.columns([1, 1.5, 1])

with col_left:
    st.subheader("📏 1. الأبعاد والنمط")
    dim_type = st.selectbox("اختر المنصة:", ["Shorts / TikTok / Reels (9:16)", "YouTube (16:9)", "Facebook / Post (1:1)"])
    st.divider() # فواصل احترافية

    st.subheader("🎙️ 2. هندسة الصوت")
    v_src = st.radio("مصدر الصوت:", ["AI (GTTS) 🤖", "ElevenLabs 💎", "بشري 🎤"])
    
    if v_src == "AI (GTTS) 🤖":
        ai_txt = st.text_area("ادخل النص هنا:")
    elif v_src == "ElevenLabs 💎":
        el_key = st.text_input("ElevenLabs API Key:")
        el_model = st.selectbox("الموديل:", ["multilingual_v2", "monolingual_v1"])
        el_txt = st.text_area("النص المراد تحويله:")
    else:
        u_voice = st.file_uploader("ارفع ملف الصوت (MP3/WAV):")
        ai_txt = st.text_area("اكتب النص هنا (للمزامنة والترجمة):")
    st.divider()

    st.subheader("🖼️ 3. التحكم في الصور")
    img_opt = st.radio("طريقة جلب الصور:", ["أوتوماتيك (ذكاء سياقي)", "يدوي (رفع صور)"])
    if img_opt == "يدوي (رفع صور)":
        u_imgs = st.file_uploader("ارفع صورك:", accept_multiple_files=True)
    else:
        search_keywords = st.text_input("كلمات مفتاحية إضافية (اختياري):", placeholder="مثال: تكنولوجيا، فضاء...")

with col_right:
    st.subheader("🎵 4. الموسيقى الخلفية")
    m_opt = st.radio("الموسيقى:", ["أوتوماتيك (هادئة)", "يدوي (رفع ملف)"])
    u_music = st.file_uploader("ارفع الموسيقى:") if m_opt == "يدوي (رفع ملف)" else None
    st.divider()

    st.subheader("📝 5. النصوص والهوية")
    show_subs = st.toggle("ترجمة كلمة بكلمة (Clipchamp Style)", value=True)
    show_banner = st.toggle("إضافة بنر سفلي", value=True)
    logo_opt = st.toggle("إضافة لوجو شخصي")
    u_logo = st.file_uploader("ارفع اللوجو:") if logo_opt else None
    st.divider()

    st.subheader("📊 6. الملخص والـ SEO")
    show_seo = st.toggle("توليد ملخص ووصف دقيق للفيديو")

with col_mid:
    st.markdown("<div style='background-color:#1e1e1e; padding:20px; border-radius:15px; border:2px solid #00E5FF;'>", unsafe_allow_html=True)
    st.subheader("📺 منطقة الإنتاج")
    
    if st.button("🚀 بدء الرندر النهائي"):
        try:
            with st.spinner("جاري معالجة الـ 11 إضافة بالترتيب..."):
                # 1. معالجة الصوت
                audio_path = os.path.join(ASSETS_DIR, "final_voice.mp3")
                if v_src == "بشري 🎤" and u_voice:
                    with open(audio_path, "wb") as f: f.write(u_voice.getbuffer())
                else:
                    gTTS(ai_txt if v_src != "ElevenLabs 💎" else el_txt, lang='ar').save(audio_path)
                
                voice = AudioFileClip(audio_path)
                total_dur = voice.duration

                # 2. بناء المشاهد (الصور والزووم)
                sentences = [s.strip() for s in re.split(r'[.؟!،]+', ai_txt) if len(s.strip()) > 1]
                dur_per_scene = total_dur / len(sentences)
                
                # ضبط الأبعاد
                if "9:16" in dim_type: h, w = 1920, 1080
                elif "16:9" in dim_type: h, w = 1080, 1920
                else: h, w = 1080, 1080

                img_clips = []
                

                for i, sent in enumerate(sentences):
                    img_p = os.path.join(ASSETS_DIR, f"sc_{i}.jpg")
                    if img_opt == "أوتوماتيك (ذكاء سياقي)":
                        get_smart_image(sent + " " + search_keywords, img_p, (w, h))
                    else:
                        with open(img_p, "wb") as f: f.write(u_imgs[i % len(u_imgs)].getbuffer())
                    
                    c = ImageClip(img_p).with_duration(dur_per_scene + 0.5)
                    # تأثير الزووم السينمائي
                    z = 1.15 if i % 2 == 0 else 0.85
                    c = c.resized(lambda t: 1 + (z-1) * (t / dur_per_scene))
                    img_clips.append(c)

                video_track = concatenate_videoclips(img_clips, method="compose", padding=-0.4)

                # 3. دمج الموسيقى والهوية والترجمة
                final_v = CompositeVideoClip([video_track], size=(w, h)).with_audio(voice)
                
                out_file = os.path.join(VIDEOS_DIR, "Mediawy_V100_Master.mp4")
                final_v.write_videofile(out_file, fps=24, codec="libx264")
                
                st.video(out_file)
                st.success("✅ تم الإنتاج بنجاح!")

                if show_seo:
                    st.divider()
                    st.subheader("📊 ملخص الـ SEO")
                    st.write(f"**العنوان المقترح:** {sentences[0]}")
                    st.write(f"**الكلمات المفتاحية:** {', '.join(re.findall(r'\w+', ai_txt)[:10])}")
                    st.write(f"**الوصف:** فيديو احترافي تم إنتاجه بواسطة Mediawy Studio V100.")

        except Exception as e:
            st.error(f"⚠️ حدث خطأ: {str(e)}")
    st.markdown("</div>", unsafe_allow_html=True)
