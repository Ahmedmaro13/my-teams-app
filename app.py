import streamlit as st
import yt_dlp
import os
import time
import shutil

# إعدادات الصفحة
st.set_page_config(page_title="Teams Downloader ☁️", page_icon="🚀")
st.title("🚀 Teams Downloader (Cloud)")

# التحقق من وجود ffmpeg (في الكلاود بيتحمل لوحده)
if not shutil.which("ffmpeg"):
    st.warning("⚠️ جاري إعداد السيرفر... انتظر دقيقة.")

# إدخال البيانات
url = st.text_input("🔗 Video URL", placeholder="Paste Teams Link Here...")
cookie = st.text_input("🍪 Cookie", placeholder="Paste Cookie Here...")
option = st.radio("Choose Format:", ("Video (MP4)", "Audio (MP3)"))

def download_media():
    timestamp = int(time.time())
    
    # مجلد مؤقت للتحميل
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
        # حفظ الملف داخل مجلد downloads
        'outtmpl': f'{download_folder}/%(title)s.%(ext)s',
    }

    if option == "Audio (MP3)":
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        ydl_opts['format'] = 'bestvideo+bestaudio/best'

    try:
        with st.spinner('⏳ Downloading... (Please wait)'):
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                # تصحيح الاسم للصوتيات
                if option == "Audio (MP3)":
                    filename = os.path.splitext(filename)[0] + ".mp3"

        st.success("✅ Finished!")
        
        # زر التحميل
        if os.path.exists(filename):
            with open(filename, "rb") as file:
                st.download_button(
                    label="📥 Download File to Device",
                    data=file,
                    file_name=os.path.basename(filename),
                    mime="audio/mpeg" if option == "Audio (MP3)" else "video/mp4"
                )
    except Exception as e:
        st.error(f"❌ Error: {e}")

if st.button("Start 🚀"):
    if url and cookie:
        download_media()
    else:
        st.warning("⚠️ Please enter URL & Cookie")