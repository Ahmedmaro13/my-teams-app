import streamlit as st
import yt_dlp
import os
import time
import shutil
import json

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Teams Smart Downloader 🧠", page_icon="🍪")

COOKIE_FILE = 'saved_cookie.json'

# --- 2. دوال حفظ واسترجاع الكوكيز ---
def load_saved_cookie():
    """تحميل الكوكي المحفوظ لو موجود"""
    if os.path.exists(COOKIE_FILE):
        try:
            with open(COOKIE_FILE, 'r') as f:
                data = json.load(f)
                return data.get("cookie", "")
        except:
            return ""
    return ""

def save_new_cookie(cookie_text):
    """حفظ الكوكي الجديد في ملف"""
    with open(COOKIE_FILE, 'w') as f:
        json.dump({"cookie": cookie_text}, f)

# --- 3. دالة التحقق من الباسورد ---
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.header("🔒 Login Required")
        st.text_input("Enter Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.header("🔒 Login Required")
        st.text_input("Enter Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        return True

# --- 4. الفوتر ---
def show_footer():
    footer_html = """
    <style>
    .footer {position: fixed; left: 0; bottom: 0; width: 100%; background-color: #0E1117; color: white; text-align: center; padding: 10px; border-top: 1px solid #333; z-index: 999;}
    .name {color: #4da6ff; font-weight: bold; text-decoration: none;}
    </style>
    <div class="footer">
        <p>Developed with ❤️ by <span class="name">Ahmed Elsayed</span> | Smart Cookie Edition</p>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

# --- 5. دوال التحميل ---
def zip_downloads(folder_path, output_filename):
    shutil.make_archive(output_filename, 'zip', folder_path)
    return f"{output_filename}.zip"

def clear_downloads(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)

# --- 6. التطبيق الرئيسي ---
def main_app():
    if st.sidebar.button("Log out 🚪"):
        st.session_state["password_correct"] = False
        st.rerun()

    st.title("🍪 Teams Smart Downloader")
    st.markdown("---")

    if not shutil.which("ffmpeg"):
        st.warning("⚠️ Server is installing FFmpeg...")

    # --- 🧠 الذكاء: تحميل الكوكي القديم ---
    saved_cookie = load_saved_cookie()
    
    # رسالة تطمين لو لقى كوكي
    if saved_cookie:
        st.success("✅ Found a saved cookie! Using it automatically.")
    else:
        st.info("ℹ️ No saved cookie found. Please enter it once.")

    # خانة الكوكيز (بتتملي لوحدها لو فيه محفوظ)
    cookie_input = st.text_input("🍪 Cookie (Auto-Saved)", value=saved_cookie, placeholder="Paste Cookie Here...")

    urls_text = st.text_area("🔗 Video URLs (Line by line)", height=150)
    option = st.radio("Choose Format:", ("Video (MP4)", "Audio (MP3)"), horizontal=True)

    # زر التشغيل
    if st.button("Start Batch Download 🚀", type="primary"):
        if not cookie_input or not urls_text.strip():
            st.warning("⚠️ Please enter Cookie and URLs!")
            return

        # 🔥 حفظ الكوكيز الجديد فوراً 🔥
        # (لو هو هو القديم هيحفظه تاني، لو اتغير هيحدثه)
        save_new_cookie(cookie_input)
        
        url_list = urls_text.strip().split('\n')
        total_links = len(url_list)
        
        download_folder = "downloads"
        clear_downloads(download_folder)

        st.info(f"🚀 Processing {total_links} files...")
        progress_bar = st.progress(0)
        status_text = st.empty()
        success_count = 0

        for i, url in enumerate(url_list):
            url = url.strip()
            if not url: continue
            
            current_num = i + 1
            status_text.markdown(f"**⏳ Processing {current_num}/{total_links}...**")
            
            ydl_opts = {
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Cookie': cookie_input, # استخدام الكوكي من الخانة
                    'Referer': 'https://aastpg.sharepoint.com/',
                },
                'restrictfilenames': True, 'windowsfilenames': True,
                'outtmpl': f'{download_folder}/{current_num}_%(title)s.%(ext)s', 'quiet': True,
            }

            if option == "Audio (MP3)":
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
            else:
                ydl_opts['format'] = 'bestvideo+bestaudio/best'

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                success_count += 1
            except Exception as e:
                st.error(f"❌ Error: {e}")
            
            progress_bar.progress(current_num / total_links)

        if success_count > 0:
            status_text.success("✅ Done! Zipping...")
            zip_file = zip_downloads(download_folder, "Lectures_Bundle")
            with open(zip_file, "rb") as f:
                st.download_button("📥 Download ZIP", f, file_name=f"Lectures_{int(time.time())}.zip", mime="application/zip")
        else:
            status_text.error("❌ Failed. Check Cookie!")

    show_footer()

# --- التشغيل ---
if check_password():
    main_app()

