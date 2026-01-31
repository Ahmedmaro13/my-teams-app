import streamlit as st
import yt_dlp
import os
import time
import shutil

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Teams Pro Batch 🔒", page_icon="📦")

# --- 2. دالة التحقق من الباسورد (Hardcoded via Secrets) ---
def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # مسح الباسورد من الذاكرة للأمان
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # أول مرة يفتح الموقع
        st.header("🔒 Login Required")
        st.text_input("Enter Admin Password", type="password", on_change=password_entered, key="password")
        show_footer()
        return False
    
    elif not st.session_state["password_correct"]:
        # باسورد غلط
        st.header("🔒 Login Required")
        st.text_input("Enter Admin Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        show_footer()
        return False
    
    else:
        # الباسورد صح
        return True

# --- 3. الفوتر ---
def show_footer():
    footer_html = """
    <style>
    .footer {position: fixed; left: 0; bottom: 0; width: 100%; background-color: #0E1117; color: white; text-align: center; padding: 10px; border-top: 1px solid #333; z-index: 999;}
    .name {color: #4da6ff; font-weight: bold; text-decoration: none;}
    </style>
    <div class="footer">
        <p>Developed with ❤️ by <span class="name">Ahmed Elsayed</span> | Pro Edition</p>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

# --- 4. دوال المساعدة ---
def zip_downloads(folder_path, output_filename):
    shutil.make_archive(output_filename, 'zip', folder_path)
    return f"{output_filename}.zip"

def clear_downloads(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)

# --- 5. التطبيق الرئيسي (Batch Logic) ---
def main_app():
    # زر الخروج
    if st.sidebar.button("Log out 🚪"):
        st.session_state["password_correct"] = False
        st.rerun()

    st.title("📦 Teams Batch Downloader")
    st.markdown("---")

    if not shutil.which("ffmpeg"):
        st.warning("⚠️ Server is installing FFmpeg... please wait.")

    # المدخلات
    cookie = st.text_input("🍪 Cookie (One for all)", placeholder="Paste Cookie Here...")
    urls_text = st.text_area("🔗 Video URLs (Paste links line by line)", height=150, placeholder="Link 1\nLink 2\nLink 3...")
    option = st.radio("Choose Format:", ("Video (MP4)", "Audio (MP3)"), horizontal=True)

    # زر التشغيل
    if st.button("Start Batch Download 🚀", type="primary"):
        if not cookie or not urls_text.strip():
            st.warning("⚠️ Please enter Cookie and URLs!")
            return

        url_list = urls_text.strip().split('\n')
        total_links = len(url_list)
        
        # تجهيز المجلدات
        download_folder = "downloads"
        clear_downloads(download_folder)

        st.info(f"🚀 Starting download for {total_links} files...")
        progress_bar = st.progress(0)
        status_text = st.empty()
        success_count = 0

        # حلقة التحميل
        for i, url in enumerate(url_list):
            url = url.strip()
            if not url: continue
            
            current_num = i + 1
            status_text.markdown(f"**⏳ Processing {current_num}/{total_links}...**")
            
            ydl_opts = {
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Cookie': cookie,
                    'Referer': 'https://aastpg.sharepoint.com/',
                },
                'restrictfilenames': True, 'windowsfilenames': True,
                'outtmpl': f'{download_folder}/%(title)s.%(ext)s', 'quiet': True,
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
                st.error(f"❌ Error in Link {current_num}: {e}")
            
            progress_bar.progress(current_num / total_links)

        # النهاية والضغط
        if success_count > 0:
            status_text.success("✅ All Done! Zipping files...")
            zip_file = zip_downloads(download_folder, "Lectures_Bundle")
            
            with open(zip_file, "rb") as f:
                st.download_button(
                    label=f"📥 Download {success_count} Files (ZIP)",
                    data=f,
                    file_name=f"Lectures_{int(time.time())}.zip",
                    mime="application/zip"
                )
        else:
            status_text.error("❌ Failed to download files.")
    
    show_footer()

# --- التشغيل ---
if check_password():
    main_app()
