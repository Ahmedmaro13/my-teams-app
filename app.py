import streamlit as st
import yt_dlp
import os
import time
import shutil

# --- 1. إعدادات الصفحة والتصميم ---
st.set_page_config(page_title="Teams Downloader 🔒", page_icon="🛡️")

# إخفاء القائمة الجانبية وعلامة Streamlit الافتراضية
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 2. دالة الفوتر (التوقيع الشيك) ---
def show_footer():
    footer_html = """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #0E1117;
        color: #FAFAFA;
        text-align: center;
        padding: 10px;
        font-family: 'Segoe UI', sans-serif;
        border-top: 1px solid #333;
        z-index: 1000;
    }
    .heart {color: #e25555;}
    .name {
        color: #4da6ff; /* لون لبني مميز للاسم */
        font-weight: bold;
        text-decoration: none;
    }
    </style>
    <div class="footer">
        <p>Developed with <span class="heart">❤</span> by <a href="#" class="name">Ahmed Elsayed</a> | Teams Downloader Pro</p>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

# --- 3. دالة التحقق من الباسورد ---
def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets["users"] and \
           st.session_state["password"] == st.secrets["users"][st.session_state["username"]]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # حذف الباسورد من الذاكرة للأمان
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # أول مرة يفتح الموقع
        st.header("🔒 Login Required")
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        show_footer()
        return False
    elif not st.session_state["password_correct"]:
        # باسورد غلط
        st.header("🔒 Login Required")
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 User not known or password incorrect")
        show_footer()
        return False
    else:
        # تم الدخول بنجاح
        return True

# --- 4. التطبيق الرئيسي (اللي كان عندك قبل كدا) ---
def main_app():
    st.title("🚀 Teams Downloader (Cloud)")
    
    # زرار لتسجيل الخروج
    if st.sidebar.button("Log out"):
        st.session_state["password_correct"] = False
        st.rerun()

    if not shutil.which("ffmpeg"):
        st.warning("⚠️ جاري إعداد السيرفر... انتظر دقيقة.")

    url = st.text_input("🔗 Video URL", placeholder="Paste Teams Link Here...")
    cookie = st.text_input("🍪 Cookie", placeholder="Paste Cookie Here...")
    option = st.radio("Choose Format:", ("Video (MP4)", "Audio (MP3)"))

    if st.button("Start 🚀"):
        if url and cookie:
            # هنا كود التحميل (مختصر للحفاظ على المساحة - هو نفس الكود السابق)
            download_media(url, cookie, option)
        else:
            st.warning("⚠️ Please enter URL & Cookie")

    show_footer()

def download_media(url, cookie, option):
    # (نفس دالة التحميل السابقة تماماً - انسخها هنا)
    timestamp = int(time.time())
    download_folder = "downloads"
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    ydl_opts = {
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Cookie': cookie,
            'Referer': 'https://aastpg.sharepoint.com/',
        },
        'restrictfilenames': True,
        'windowsfilenames': True,
        'outtmpl': f'{download_folder}/%(title)s.%(ext)s',
    }

    if option == "Audio (MP3)":
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
    else:
        ydl_opts['format'] = 'bestvideo+bestaudio/best'

    try:
        with st.spinner('⏳ Downloading... (Please wait)'):
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if option == "Audio (MP3)": filename = os.path.splitext(filename)[0] + ".mp3"

        if os.path.exists(filename):
            with open(filename, "rb") as file:
                st.success("✅ Finished!")
                st.download_button(label="📥 Download File", data=file, file_name=os.path.basename(filename), mime="application/octet-stream")
    except Exception as e:
        st.error(f"❌ Error: {e}")

# --- 5. التشغيل ---
if check_password():
    main_app()
