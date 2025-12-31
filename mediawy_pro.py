import streamlit as st
import os, requests, re, io, random
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips

# --- 1. إعداد الاستوديو ---
MEDIA_DIR = "Mediawy_Studio_V109"
ASSETS_DIR = os.path.join(MEDIA_DIR, "Assets")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "Videos")
for d in [ASSETS_DIR, VIDEOS_DIR]: os.makedirs(d, exist_ok=True)

# --- دالة صنع البنر الجرافيكي السفلي ---
def create_graphic_banner(size, text):
    w, h = size
    b_h = int(h * 0.12)
    banner = Image.new("RGBA", (w, b_h), (0, 0, 0, 180)) 
    draw = ImageDraw.Draw(banner)
    draw.line([(0, 0), (w, 0)], fill="#007BFF", width=5) # خط أزرق فني
    try: font = ImageFont.truetype("arial.ttf", b_h // 3)
    except: font = ImageFont.load_default()
    draw.text((w // 2, b_h // 2), text, font=font, fill="white", anchor="mm")
    path = os.path.join(ASSETS_DIR, "banner.png")
    banner.save(path)
    return path

# --- واجهة المستخدم البيضاء الاحترافية ---
st.set_page_config(page_title="Mediawy V109 Pro", layout="wide")
st.markdown("<style>.stApp { background-color: #FFFFFF; color: #333; } .render-box { border: 2px solid #007BFF; padding: 20px; border-radius: 15px; background: #F8F9FA; }</style>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center; color:#007BFF;'>🎬 Mediawy Studio V109</h1>", unsafe_allow_html=True)

col_right, col_mid, col_left = st.columns([1, 1.8, 1])

with col_right:
    st.markdown("## 🎙️ 1. هندسة الصوت")
    v_src = st.radio("المصدر:", ["بشري 🎤", "AI 🤖", "ElevenLabs 💎"], index=0)
    
    if v_src == "بشري 🎤":
        u_voice = st.file_uploader("📥 ارفع صوتك المسجل هنا (MP3/WAV):")
    elif v_src == "ElevenLabs 💎":
        st.text_input("🔑 API Key")
        st.text_input("📦 Model ID")
        
    voice_text = st.text_area("✍️ جدول النص (اكتب ما يقال في الصوت):", placeholder="هذا النص ضروري للترجمة واختيار الصور...")
    st.divider()
    st.markdown("## 📏 2. الأبعاد")
    platform = st.selectbox("المقاس:", ["Shorts (9:16)", "YouTube (16:9)", "Post (1:1)"])

with col_left:
    st.markdown("## 🎭 3. نمط المونتاج")
    m_style = st.selectbox("الروح:", ["سينمائي 🎬", "درامي 🎭", "وثائقي 🎞️"])
    st.divider()
    st.markdown("## 🎨 4. الهوية")
    use_logo = st.toggle("إضافة لوجو")
    u_logo = st.file_uploader("🖼️ تحميل اللوجو") if use_logo else None
    use_banner = st.toggle("تفعيل البنر السفلي")
    banner_txt = st.text_input("نص البنر:", "Mediawy Production") if use_banner else ""
    st.divider()
    st.markdown("## 🖼️ 5. الصور")
    img_mode = st.radio("الجلب:", ["أوتوماتيك 🤖", "يدوي 📁"])
    u_imgs = st.file_uploader("📁 تحميل الصور يدوي", accept_multiple_files=True) if img_mode == "يدوي 📁" else None

with col_mid:
    st.markdown("<div class='render-box'>", unsafe_allow_html=True)
    st.subheader("📺 شاشة الإنتاج")
    
    if st.button("🚀 بدء الإنتاج الاحترافي"):
        if v_src == "بشري 🎤" and not u_voice:
            st.error("⚠️ من فضلك ارفع ملف الصوت أولاً!")
        elif not voice_text:
            st.error("⚠️ اكتب النص في الجدول للمزامنة والترجمة!")
        else:
            try:
                with st.spinner("جاري رندر الفيديو بالصوت البشري..."):
                    # 1. تجهيز الصوت
                    v_p = os.path.join(ASSETS_DIR, "final_audio.mp3")
                    if v_src == "بشري 🎤":
                        with open(v_p, "wb") as f: f.write(u_voice.getbuffer())
                    else:
                        gTTS(voice_text, lang='ar').save(v_p)
                    audio_clip = AudioFileClip(v_p)

                    # 2. الأبعاد والمشاهد
                    w, h = (1080, 1920) if "9:16" in platform else (1920, 1080)
                    sentences = [s.strip() for s in re.split(r'[.؟!،]+', voice_text) if len(s.strip()) > 1]
                    dur_per_scene = audio_clip.duration / len(sentences)
                    
                    clips = []
                    for i, sent in enumerate(sentences):
                        img_p = os.path.join(ASSETS_DIR, f"i_{i}.jpg")
                        if img_mode == "أوتوماتيك 🤖":
                            resp = requests.get(f"https://picsum.photos/seed/{i}/{w}/{h}")
                            Image.open(io.BytesIO(resp.content)).save(img_p)
                        else:
                            with open(img_p, "wb") as f: f.write(u_imgs[i % len(u_imgs)].getbuffer())
                        
                        # تأثير الزووم حسب النمط
                        c = ImageClip(img_p).with_duration(dur_per_scene).resized(lambda t: 1 + 0.1 * (t / dur_per_scene))
                        clips.append(c)

                    main_video = concatenate_videoclips(clips, method="compose")

                    # 3. دمج الطبقات (اللوجو والبنر فوق الفيديو)
                    layers = [main_video]
                    
                    if use_banner:
                        b_p = create_graphic_banner((w, h), banner_txt)
                        layers.append(ImageClip(b_p).with_duration(audio_clip.duration).with_position(("center", "bottom")))
                    
                    if use_logo and u_logo:
                        l_p = os.path.join(ASSETS_DIR, "logo.png")
                        img_l = Image.open(u_logo).convert("RGBA")
                        img_l.thumbnail((w // 6, h // 6))
                        img_l.save(l_p)
                        layers.append(ImageClip(l_p).with_duration(audio_clip.duration).with_position((w - (w//6) - 30, 30)))

                    final_video = CompositeVideoClip(layers, size=(w, h)).with_audio(audio_clip)
                    out_path = os.path.join(VIDEOS_DIR, "Mediawy_V109.mp4")
                    final_video.write_videofile(out_path, fps=24, codec="libx264")
                    
                    st.video(out_path)
                    st.success("🎯 تم الإنتاج بنجاح بالصوت البشري!")
                    
                    # الـ SEO
                    st.divider()
                    st.markdown("### 📊 6. ملخص الـ SEO")
                    st.info(f"**الاسم:** {sentences[0]}\n\n**الكلمات:** {sentences[0][:20]}\n\n**الوصف:** فيديو احترافي بنمط {m_style}.")

            except Exception as e:
                st.error(f"حدث خطأ: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
