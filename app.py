import streamlit as st
import yt_dlp
import os
import time
import shutil
import json

st.set_page_config(page_title="Teams Simple Fix 🔧", page_icon="🛠️")

COOKIE_FILE = 'saved_cookie.json'
ZIP_NAME = "Lectures_Bundle" 

def load_saved_cookie():
    if os.path.exists(COOKIE_FILE):
        try:
            with open(COOKIE_FILE, 'r') as f:
                data = json.load(f)
                return data.get("cookie", "")
        except:
            return ""
    return ""

def save_new_cookie(cookie_text):
    with open(COOKIE_FILE, 'w') as f:
        json.dump({"cookie": cookie_text}, f)

def clear_downloads(folder_path):
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
        except:
            pass # طنش لو معرفش يمسح
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def zip_downloads(folder_path, output_filename):
    shutil.make_archive(output_filename, 'zip', folder_path)
    return f"{output_filename}.zip"

def main_app():
    st.title("📦 Teams Downloader (Direct Mode)")
    
    if not shutil.which("ffmpeg"):
        st.warning("⚠️ Server is installing FFmpeg...")

    saved_cookie = load_saved_cookie()
    cookie_input = st.text_input("🍪 Cookie (Paste NEW one here)", value=saved_cookie)
    
    if st.button("Save Cookie 💾"):
        save_new_cookie(cookie_input)
        st.success("Saved!")
        time.sleep(0.5)
        st.rerun()

    urls_text = st.text_area("🔗 Video URLs", height=150)
    
    # رجعنا للاختيار البسيط المباشر
    format_option = st.selectbox("Format:", ["Video (720p)", "Video (480p)", "Audio (MP3)"])

    if st.button("Start Download 🚀", type="primary"):
        cookie = cookie_input or saved_cookie
        url_list = urls_text.strip().split('\n')
        
        clear_downloads("downloads")
        st.info("🚀 Starting...")
        
        progress = st.progress(0)
        
        for i, url in enumerate(url_list):
            if not url.strip(): continue
            
            # إعدادات بسيطة جداً ومباشرة (زي أول نسخة اشتغلت)
            ydl_opts = {
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                    'Cookie': cookie, # رجعنا الكوكيز هنا مباشر
                    'Referer': 'https://aastpg.sharepoint.com/',
                },
                'outtmpl': f'downloads/{i+1}_%(title)s.%(ext)s',
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True, # عشان لو لينك باظ يكمل اللي بعده
            }

            if "Audio" in format_option:
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}]
            elif "480p" in format_option:
                # محاولة تحميل 480 بأبسط طريقة
                ydl_opts['format'] = 'bestvideo[height<=480]+bestaudio/best[height<=480]/best'
            else:
                # 720p
                ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]/best'

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except Exception as e:
                st.error(f"Error: {e}")
            
            progress.progress((i + 1) / len(url_list))

        # الضغط والتحميل
        try:
            zip_file = zip_downloads("downloads", ZIP_NAME)
            with open(zip_file, "rb") as f:
                st.download_button("📥 Download ZIP", f, file_name="Lectures.zip")
        except:
            st.warning("No files downloaded. Check cookie!")

if __name__ == "__main__":
    main_app()
