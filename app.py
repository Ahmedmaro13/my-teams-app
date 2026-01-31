import streamlit as st
import yt_dlp
import os
import time
import shutil

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Teams Batch Downloader 📦", page_icon="🚀")
st.title("🚀 Teams Batch Downloader")

# --- دالة ضغط الملفات (ZIP) ---
def zip_downloads(folder_path, output_filename):
    shutil.make_archive(output_filename, 'zip', folder_path)
    return f"{output_filename}.zip"

# --- دالة تنظيف المجلد ---
def clear_downloads(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)

# --- الواجهة ---
if not shutil.which("ffmpeg"):
    st.warning("⚠️ جاري إعداد السيرفر... انتظر دقيقة.")

# 1. إدخال الكوكيز (مرة واحدة للكل)
cookie = st.text_input("🍪 Cookie (One for all)", placeholder="Paste Cookie Here...")

# 2. إدخال الروابط (مربع كبير)
urls_text = st.text_area("🔗 Video URLs (Link per line)", height=150, placeholder="Link 1\nLink 2\nLink 3...")

# 3. الخيارات
option = st.radio("Choose Format:", ("Video (MP4)", "Audio (MP3)"))

# --- زر التشغيل ---
if st.button("Start Batch Download 🚀"):
    if not cookie or not urls_text.strip():
        st.warning("⚠️ Please enter Cookie and at least one URL")
    else:
        # تحويل النص لقائمة روابط
        url_list = urls_text.strip().split('\n')
        total_links = len(url_list)
        
        st.info(f"📦 Found {total_links} links. Starting process...")
        
        # تجهيز المجلد
        download_folder = "downloads"
        clear_downloads(download_folder) # تنظيف القديم

        # شريط تقدم عام
        progress_bar = st.progress(0)
        status_text = st.empty()

        success_count = 0
        
        # --- بداية اللوب (Loop) ---
        for i, url in enumerate(url_list):
            url = url.strip()
            if not url: continue # تخطي الأسطر الفارغة
            
            current_num = i + 1
            status_text.write(f"⏳ Processing {current_num}/{total_links}...")
            
            # إعدادات التحميل (نفس القديمة)
            ydl_opts = {
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Cookie': cookie,
                    'Referer': 'https://aastpg.sharepoint.com/',
                },
                'restrictfilenames': True,
                'windowsfilenames': True,
                'outtmpl': f'{download_folder}/%(title)s.%(ext)s',
                'quiet': True, # عشان ميعملش دوشة في اللوج
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
                st.error(f"❌ Failed Link {current_num}: {e}")
            
            # تحديث شريط التقدم
            progress_bar.progress(current_num / total_links)

        # --- النهاية ---
        if success_count > 0:
            st.success(f"✅ Completed! {success_count}/{total_links} files downloaded.")
            
            # ضغط الملفات كلها في ملف واحد
            status_text.write("🗜️ Zipping files... please wait.")
            zip_file = zip_downloads(download_folder, "My_Lectures")
            
            # زر تحميل الـ ZIP
            with open(zip_file, "rb") as f:
                st.download_button(
                    label="📥 Download All (ZIP)",
                    data=f,
                    file_name=f"Lectures_Batch_{int(time.time())}.zip",
                    mime="application/zip"
                )
        else:
            st.error("❌ No files were downloaded successfully.")
