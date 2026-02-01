import streamlit as st
import yt_dlp
import os
import time
import shutil
import json

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Teams VIP 📦", page_icon="🚀")

COOKIE_FILE = 'saved_cookie.json'
TEMP_COOKIE_FILE = 'temp_cookies.txt'
ZIP_NAME = "Lectures_Bundle" 

# --- دوال مساعدة ---
def load_saved_cookie():
    if os.path.exists(COOKIE_FILE):
        try:
            with open(COOKIE_FILE, 'r') as f:
                return json.load(f).get("cookie", "")
        except: return ""
    return ""

def save_new_cookie(cookie_text):
    with open(COOKIE_FILE, 'w') as f:
        json.dump({"cookie": cookie_text}, f)

def create_netscape_cookie_file(raw_cookie_str):
    domain = ".sharepoint.com"
    with open(TEMP_COOKIE_FILE, 'w') as f:
        f.write("# Netscape HTTP Cookie File\n\n")
        if raw_cookie_str:
            for item in raw_cookie_str.split(';'):
                if '=' in item:
                    try:
                        name, value = item.strip().split('=', 1)
                        f.write(f"{domain}\tTRUE\t/\tTRUE\t2147483647\t{name}\t{value}\n")
                    except: continue
    return TEMP_COOKIE_FILE

def clear_downloads(folder_path):
    # دالة تنظيف "ناعمة" عشان متهنجش البرنامج
    if os.path.exists(folder_path):
        try: shutil.rmtree(folder_path)
        except: pass 
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def zip_downloads(folder_path, output_filename):
    shutil.make_archive(output_filename, 'zip', folder_path)
    return f"{output_filename}.zip"

def is_file_valid(folder_path):
    # حساس لاكتشاف الملفات المضروبة (صفحات الـ Login)
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            try:
                file_path = os.path.join(root, file)
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                if size_mb < 0.8: # لو أقل من 1 ميجا يبقى بايظ
                    return False, size_mb
            except: pass
    return True, 0

# --- التطبيق الرئيسي ---
def main_app():
    st.title("📦 Teams VIP (Ultimate Fix)")
    
    if not shutil.which("ffmpeg"):
        st.warning("⚠️ Server is installing FFmpeg...")

    saved_cookie = load_saved_cookie()
    
    # 1. الكوكيز
    cookie_input = st.text_input("🍪 Cookie (Use Incognito Mode for best results!)", value=saved_cookie)
    if st.button("Save Cookie 💾"):
        save_new_cookie(cookie_input)
        st.success("Cookie Saved!")
        time.sleep(0.5)
        st.rerun()

    # 2. الروابط
    urls_text = st.text_area("🔗 Video URLs (Line by line)", height=150)
    
    # 3. الجودة (تم إصلاح مشكلة 480p)
    quality = st.radio("Quality:", ["Video (720p - HD)", "Video (480p - Fast)", "Audio (MP3)"], horizontal=True)

    if st.button("Start Download 🚀", type="primary"):
        final_cookie = cookie_input or saved_cookie
        
        # تنظيف أي بقايا قديمة
        try: os.remove(f"{ZIP_NAME}.zip")
        except: pass
        
        create_netscape_cookie_file(final_cookie)
        download_folder = "downloads"
        clear_downloads(download_folder)
        
        url_list = urls_text.strip().split('\n')
        total = len(url_list)
        
        st.info(f"Starting download for {total} files...")
        prog_bar = st.progress(0)
        status = st.empty()
        
        cookie_dead = False
        success = 0

        for i, url in enumerate(url_list):
            if not url.strip(): continue
            if cookie_dead: break
            
            current = i + 1
            status.markdown(f"**⏳ Processing {current}/{total}...**")
            
            # إعدادات التحميل المتقدمة
            ydl_opts = {
                'cookiefile': TEMP_COOKIE_FILE,
                'outtmpl': f'{download_folder}/{current}_%(title)s.%(ext)s',
                'quiet': True,
                'no_warnings': True,
                # أهم سطرين لحل مشكلة 480p وتجميع الفيديو
                'merge_output_format': 'mp4',
                'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'},
            }

            # تخصيص الجودة
            if "Audio" in quality:
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}]
            elif "480p" in quality:
                # يقبل أي صيغة فيديو <= 480 ويدمجها MP4
                ydl_opts['format'] = 'bestvideo[height<=480]+bestaudio/best[height<=480]/best'
            else:
                # 720p
                ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]/best'

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # فحص الحساس الذكي
                valid, size = is_file_valid(download_folder)
                if not valid:
                    st.error(f"🚨 **STOP! Cookie Expired.**")
                    st.error(f"⚠️ Downloaded a fake file ({size:.2f} MB). Please get a NEW cookie from Incognito mode.")
                    cookie_dead = True
                    break
                
                success += 1
            except Exception as e:
                st.error(f"Error in link {current}: {e}")
            
            prog_bar.progress(current / total)

        # الختام
        if cookie_dead:
            clear_downloads(download_folder) # امسح الملف البايظ
        elif success > 0:
            status.success("✅ Done! Zipping...")
            zip_path = zip_downloads(download_folder, ZIP_NAME)
            with open(zip_path, "rb") as f:
                st.download_button("📥 Download ZIP", f, file_name=f"Lectures_{int(time.time())}.zip")
        else:
            status.error("❌ No files downloaded.")

if __name__ == "__main__":
    main_app()
