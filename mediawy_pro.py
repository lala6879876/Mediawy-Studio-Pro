import streamlit as st
import os, requests, re, io, random
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip, vfx

# --- 1. إعداد الاستوديو ---
MEDIA_DIR = "Mediawy_Final_Pro"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- واجهة المستخدم الاحترافية (Design System) ---
st.set_page_config(page_title="Mediawy V103 Master", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #05070a; }
    [data-testid="stSidebar"] { background-color: #0d1117; border-right: 2px solid #00E5FF; }
    .main-box { border: 2px solid #00E5FF; padding: 20px; border-radius: 15px; background: #0d1117; }
    .stDivider { border-bottom: 2px solid #1f2937; }
    h2 { color: #00E5FF !important; border-bottom: 1px solid #00E5FF; padding-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- توزيع الاستوديو (3 أعمدة) ---
col_right, col_mid, col_left = st.columns([1, 1.8, 1])

# --- العمود الأيمن: هندسة الصوت والأبعاد ---
with col_right:
    st.markdown("## 📏 1. الأبعاد والمنصة")
    platform = st.selectbox("اختر المقاس:", ["Shorts / TikTok (9:16)", "YouTube Standard (16:9)", "Facebook / Post (1:1)"])
    
    st.divider()
    
    st.markdown("## 🎙️ 2. هندسة الصوت")
    v_src = st.radio("المصدر:", ["AI (GTTS) 🤖", "ElevenLabs 💎", "بشري 🎤"])
    
    if v_src == "AI (GTTS) 🤖":
        ai_text = st.text_area("✍️ جدول النص (AI):")
    elif v_src == "ElevenLabs 💎":
        el_key = st.text_input("🔑 مفتاح API (Key):")
        el_model = st.text_input("📦 الموديل (Model):")
        ai_text = st.text_area("✍️ جدول النص (ElevenLabs):")
    else:
        u_voice = st.file_uploader("🎤 أيقونة تحميل الصوت البشري:")
        ai_text = st.text_area("✍️ النص (للمزامنة والترجمة):")
    
    st.divider()
    
    st.markdown("## 🎭 3. نمط المونتاج")
    m_style = st.select_slider("اختر الروح:", ["وثائقي", "درامي", "سينمائي"])

# --- العمود الأيسر: الصور والموسيقى والهوية ---
with col_left:
    st.markdown("## 🖼️ 4. محرك الصور")
    img_opt = st.radio("طريقة الجلب:", ["أوتوماتيك (سياقي)", "يدوي (رفع)"])
    if img_opt == "يدوي (رفع)":
        u_imgs = st.file_uploader("📁 أيقونة تحميل الصور:", accept_multiple_files=True)
    else:
        keywords = st.text_input("🔍 مربع الكلمات المفتاحية:", placeholder="اكتب سياق الصور هنا...")

    st.divider()
    
    st.markdown("## 🎵 5. الموسيقى")
    m_opt = st.radio("الموسيقى:", ["أوتوماتيك", "يدوي"])
    u_music = st.file_uploader("🎵 أيقونة تحميل الموسيقى:") if m_opt == "يدوي" else None

    st.divider()
    
    st.markdown("## 🎨 6. الهوية والترجمة")
    show_subs = st.toggle("🔤 ترجمة كلمة بكلمة", value=True)
    show_banner = st.toggle("🏁 بنر سفلي")
    use_logo = st.toggle("🖼️ إضافة لوجو")
    u_logo = st.file_uploader("أيقونة تحميل اللوجو:") if use_logo else None

# --- العمود الأوسط: شاشة العرض والإنتاج والـ SEO ---
with col_mid:
    st.markdown("<div class='main-box'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>📺 شاشة الإنتاج المركزي</h2>", unsafe_allow_html=True)
    
    
    
    if st.button("🚀 إطلاق الإنتاج الملياري"):
        if not ai_text:
            st.error("⚠️ برجاء إدخال النص في جداول الصوت أولاً!")
        else:
            try:
                with st.spinner(f"جاري معالجة فيديو {m_style} بمواصفات V103..."):
                    # [معالجة الصوت]
                    v_p = os.path.join(ASSETS_DIR, "v.mp3")
                    if v_src == "بشري 🎤" and u_voice:
                        with open(v_p, "wb") as f: f.write(u_voice.getbuffer())
                    else:
                        gTTS(ai_text, lang='ar').save(v_p)
                    voice = AudioFileClip(v_p)

                    # [ضبط الأبعاد]
                    if "9:16" in platform: w, h = 1080, 1920
                    elif "16:9" in platform: w, h = 1920, 1080
                    else: w, h = 1080, 1080

                    # [بناء المشاهد]
                    sentences = [s.strip() for s in re.split(r'[.؟!،]+', ai_text) if len(s.strip()) > 1]
                    dur = voice.duration / len(sentences)
                    clips = []
                    
                    for i, sent in enumerate(sentences):
                        img_p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
                        if img_opt == "أوتوماتيك (سياقي)":
                            q = keywords if keywords else sent[:20]
                            resp = requests.get(f"https://source.unsplash.com/featured/{w}x{h}/?{q}&sig={i}")
                            Image.open(io.BytesIO(resp.content)).convert("RGB").save(img_p)
                        else:
                            with open(img_p, "wb") as f: f.write(u_imgs[i % len(u_imgs)].getbuffer())
                        
                        c = ImageClip(img_p).with_duration(dur)
                        # زووم سينمائي حسب النمط
                        z = 1.2 if m_style == "سينمائي" else 1.1
                        c = c.resized(lambda t: 1 + (z-1) * (t / dur))
                        clips.append(c)

                    video = concatenate_videoclips(clips, method="compose")
                    
                    # [الهوية]
                    final_layers = [video]
                    if use_logo and u_logo:
                        lp = os.path.join(ASSETS_DIR, "l.png")
                        Image.open(u_logo).resize((w//7, w//7)).save(lp)
                        final_layers.append(ImageClip(lp).with_duration(voice.duration).with_position(("right", "top")))

                    final_vid = CompositeVideoClip(final_layers, size=(w, h)).with_audio(voice)
                    out = os.path.join(VIDEOS_DIR, "V103_Master.mp4")
                    final_vid.write_videofile(out, fps=24, codec="libx264")
                    
                    st.video(out)
                    st.success("🎯 تم الإنتاج بنجاح!")
                    
                    # [قسم الملخص والـ SEO]
                    st.divider()
                    st.markdown("## 📊 7. ملخص الفيديو والـ SEO")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**الاسم المقترح:** {sentences[0]}")
                        st.info(f"**الكلمات المفتاحية:** {keywords if keywords else 'تلقائي'}")
                    with col2:
                        st.info(f"**الوصف:** فيديو {m_style} احترافي تم إنتاجه عبر Mediawy Master.")
            
            except Exception as e:
                st.error(f"خطأ: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
