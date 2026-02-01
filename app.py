import streamlit as st
import yt_dlp
import os
import time
import shutil
import json

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Teams Pro Batch 📦", page_icon="🚀")

COOKIE_FILE = 'saved_cookie.json'
ZIP_NAME = "Lectures_Bundle" # الاسم الثابت للملف المضغوط

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

# --- 3. دالة التحقق من الباسورد (Secrets) ---
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.header("🔒 Login Required")
        st.text_input("Enter Admin Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.header("🔒 Login Required")
        st.text_input("Enter Admin Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        return True

# --- 4. الفوتر (توقيعك) ---
def show_footer():
    footer_html = """
    <style>
    .footer {position: fixed; left: 0; bottom: 0; width: 100%; background-color: #0E1117; color: white; text-align: center; padding: 10px; border-top: 1px solid #333; z-index: 999;}
    .name {color: #4da6ff; font-weight: bold; text-decoration: none;}
    </style>
    <div class="footer">
        <p>Developed with ❤️ by <span class="name">Ahmed Elsayed</span> | Pro Batch Edition</p>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

# --- 5. دوال مساعدة (Zip & Clear) ---
def zip_downloads(folder_path, output_filename):
    # الدالة دي بتعمل ملف zip باسم output_filename.zip
    shutil.make_archive(output_filename, 'zip', folder_path)
    return f"{output_filename}.zip"

def clear_downloads(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)

# --- 6. التطبيق الرئيسي ---
def main_app():
    # زر الخروج
    if st.sidebar.button("Log out 🚪"):
        st.session_state["password_correct"] = False
        st.rerun()

    st.title("📦 Teams Batch Downloader")
    st.markdown("---")

    # التأكد من FFmpeg
    if not shutil.which("ffmpeg"):
        st.warning("⚠️ Server is installing FFmpeg... please wait.")

    # تحميل الكوكي القديم
    saved_cookie = load_saved_cookie()
    
    # === القسم الأول: إعدادات الكوكيز ===
    st.subheader("1️⃣ Configuration")
    
    cookie_input = st.text_input("🍪 Cookie (Paste here)", value=saved_cookie)
    
    # زرار الحفظ المستقل
    if st.button("Save Cookie Only 💾"):
        if cookie_input.strip():
            save_new_cookie(cookie_input)
            st.success("✅ Cookie saved successfully!")
            time.sleep(1) 
            st.rerun() # تحديث الصفحة لتأكيد الحفظ
        else:
            st.warning("⚠️ Cookie field is empty!")

    st.markdown("---")

    # === القسم الثاني: التحميل ===
    st.subheader("2️⃣ Downloads")

    # 🔥 ميزة استعادة التحميل (Resume) 🔥
    # لو فيه ملف zip موجود من قبل كدة (مثلاً النت قطع)، اظهره علطول
    existing_zip = f"{ZIP_NAME}.zip"
    if os.path.exists(existing_zip):
        st.info("💡 **Found a finished download!** (Did you refresh? You can download it now)")
        with open(existing_zip, "rb") as f:
            st.download_button(
                label="🔄 Resume Download (Last Zip)",
                data=f,
                file_name=f"Lectures_Recovered_{int(time.time())}.zip",
                mime="application/zip",
                type="secondary"
            )
        st.markdown("---")

    urls_text = st.text_area("🔗 Video URLs (Paste links line by line)", height=150)
    option = st.radio("Choose Format:", ("Video (MP4)", "Audio (MP3)"), horizontal=True)

    # زرار بدء التحميل
    if st.button("Start Batch Download 🚀", type="primary"):
        # بنستخدم الكوكي اللي في الخانة، أو المحفوظ لو الخانة فاضية
        final_cookie = cookie_input or saved_cookie
        
        if not final_cookie:
            st.error("⚠️ Please save a cookie first in Step 1!")
            return
            
        if not urls_text.strip():
            st.warning("⚠️ Please enter video URLs in Step 2!")
            return

        # حفظ الكوكيز احتياطي
        save_new_cookie(final_cookie)
        
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
                    'Cookie': final_cookie,
                    'Referer': 'https://aastpg.sharepoint.com/',
                },
                'restrictfilenames': True, 'windowsfilenames': True,
                # 🔥 الترقيم لمنع استبدال الملفات 🔥
                'outtmpl': f'{download_folder}/{current_num}_%(title)s.%(ext)s', 
                'quiet': True,
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
            
            # ضغط الملفات بالاسم الثابت عشان نقدر نسترجعه لو النت قطع
            zip_file = zip_downloads(download_folder, ZIP_NAME)
            
            with open(zip_file, "rb") as f:
                st.download_button(
                    label=f"📥 Download {success_count} Files (ZIP)",
                    data=f,
                    file_name=f"Lectures_{int(time.time())}.zip",
                    mime="application/zip"
                )
        else:
            status_text.error("❌ Failed to download files. Check your Cookie!")

    show_footer()

# --- التشغيل ---
if check_password():
    main_app()
