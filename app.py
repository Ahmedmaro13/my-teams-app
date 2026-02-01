import streamlit as st
import yt_dlp
import os
import time
import shutil
import json

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Teams VIP 📦", page_icon="🚀")

COOKIE_FILE = 'saved_cookie.json'
TEMP_COOKIE_FILE = 'temp_cookies.txt'
ZIP_NAME = "Lectures_Bundle" 

# --- 2. دوال حفظ واسترجاع الكوكيز ---
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

def create_netscape_cookie_file(raw_cookie_str):
    domain = ".sharepoint.com"
    with open(TEMP_COOKIE_FILE, 'w') as f:
        f.write("# Netscape HTTP Cookie File\n")
        f.write("# This is a generated file!  Do not edit.\n\n")
        if raw_cookie_str:
            for item in raw_cookie_str.split(';'):
                if '=' in item:
                    try:
                        name, value = item.strip().split('=', 1)
                        f.write(f"{domain}\tTRUE\t/\tTRUE\t2147483647\t{name}\t{value}\n")
                    except:
                        continue
    return TEMP_COOKIE_FILE

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
        st.text_input("Enter Admin Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.header("🔒 Login Required")
        st.text_input("Enter Admin Password", type="password", on_change=password_entered, key="password")
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
        <p>Developed with ❤️ by <span class="name">Ahmed Elsayed</span> | Pro Batch Edition</p>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

# --- 5. دوال مساعدة ---
def zip_downloads(folder_path, output_filename):
    shutil.make_archive(output_filename, 'zip', folder_path)
    return f"{output_filename}.zip"

def clear_downloads(folder_path):
    """🔥 دالة التنظيف الآمنة لمنع الـ OSError 🔥"""
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path) # حاول تمسح الفولدر
        except Exception:
            # لو الفولدر معلق، حاول تمسح الملفات اللي جواه واحد واحد
            try:
                for filename in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, filename)
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
            except:
                pass # لو فشل خالص، كمل ولا يهمك
            
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def is_file_valid(folder_path):
    """🔥 الحساس الذكي لاكتشاف الكوكيز الميتة 🔥"""
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            # لو الملف أصغر من 1 ميجا يبقى ده HTML Login Page
            if size_mb < 1.0: 
                return False, size_mb
    return True, 0

# --- 6. التطبيق الرئيسي ---
def main_app():
    if st.sidebar.button("Log out 🚪"):
        st.session_state["password_correct"] = False
        st.rerun()

    st.title("📦 Teams VIP")
    st.markdown("---")

    if not shutil.which("ffmpeg"):
        st.warning("⚠️ Server is installing FFmpeg... please wait.")

    saved_cookie = load_saved_cookie()
    
    # === القسم الأول: الكوكيز ===
    st.subheader("1️⃣ Configuration")
    cookie_input = st.text_input("🍪 Cookie (Paste here)", value=saved_cookie)
    
    if st.button("Save Cookie Only 💾"):
        if cookie_input.strip():
            save_new_cookie(cookie_input)
            st.success("✅ Cookie saved successfully!")
            time.sleep(1) 
            st.rerun() 
        else:
            st.warning("⚠️ Cookie field is empty!")

    st.markdown("---")

    # === القسم الثاني: التحميل ===
    st.subheader("2️⃣ Downloads")

    # استعادة التحميل السابق (لو موجود)
    existing_zip = f"{ZIP_NAME}.zip"
    if os.path.exists(existing_zip):
        try:
            with open(existing_zip, "rb") as f:
                st.info("💡 **Found a finished download!** (You can download it now)")
                st.download_button(label="🔄 Resume Download (Last Zip)", data=f, file_name=f"Lectures_Recovered_{int(time.time())}.zip", mime="application/zip", type="secondary")
            st.markdown("---")
        except:
            # لو الملف بايظ امسحه
            try: os.remove(existing_zip)
            except: pass

    urls_text = st.text_area("🔗 Video URLs (Paste links line by line)", height=150)
    
    # خيارات الجودة
    format_option = st.radio(
        "Choose Quality:",
        ("🎥 Video (720p - HD)", "📱 Video (480p - Fast)", "🎧 Audio Only (MP3)"),
        horizontal=True
    )

    if st.button("Start Download 🚀", type="primary"):
        final_cookie = cookie_input or saved_cookie
        
        if not final_cookie:
            st.error("⚠️ Please save a cookie first in Step 1!")
            return
            
        if not urls_text.strip():
            st.warning("⚠️ Please enter video URLs in Step 2!")
            return

        # 🔥 خطوة مهمة: مسح الـ Zip القديم عشان نبدأ على نظافة
        if os.path.exists(existing_zip):
            try: os.remove(existing_zip)
            except: pass

        save_new_cookie(final_cookie)
        create_netscape_cookie_file(final_cookie)
        
        url_list = urls_text.strip().split('\n')
        total_links = len(url_list)
        
        download_folder = "downloads"
        clear_downloads(download_folder)

        st.info(f"🚀 Starting download for {total_links} files...")
        progress_bar = st.progress(0)
        status_text = st.empty()
        success_count = 0
        cookie_died = False

        for i, url in enumerate(url_list):
            url = url.strip()
            if not url: continue
            
            # لو الكوكيز مات، وقف اللوب فوراً
            if cookie_died: break

            current_num = i + 1
            status_text.markdown(f"**⏳ Processing {current_num}/{total_links}...**")
            
            ydl_opts = {
                'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                'cookiefile': TEMP_COOKIE_FILE,
                'restrictfilenames': True, 
                'windowsfilenames': True,
                'outtmpl': f'{download_folder}/{current_num}_%(title)s.%(ext)s', 
                'quiet': True,
                'no_warnings': True,
            }

            # 🔥 ضبط الجودة (Fix for 480p & OSError) 🔥
            if "Audio" in format_option:
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
            
            elif "480p" in format_option:
                # التعديل الحاسم: شيلنا [ext=mp4] وضفنا merge_output_format
                ydl_opts['format'] = 'bestvideo[height<=480]+bestaudio/best[height<=480]/best'
                ydl_opts['merge_output_format'] = 'mp4'
            
            else:
                ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]/best'
                ydl_opts['merge_output_format'] = 'mp4'

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # 🔥 تشغيل الحساس الذكي 🔥
                valid, size = is_file_valid(download_folder)
                if not valid:
                    st.error(f"🚨 **STOP! Cookie is DEAD.**")
                    st.error(f"⚠️ Downloaded file is only {size:.2f} MB (Fake Login Page).")
                    st.error("👉 Refresh browser -> Network -> Use 'Doc' filter -> Get Headers Cookie.")
                    
                    clear_downloads(download_folder) # امسح الفوضى
                    cookie_died = True
                    break # اخرج من اللوب
                
                success_count += 1
                
            except Exception as e:
                st.error(f"❌ Error in Link {current_num}: {e}")
            
            progress_bar.progress(current_num / total_links)

        # تنظيف الملفات المؤقتة
        if os.path.exists(TEMP_COOKIE_FILE):
            try: os.remove(TEMP_COOKIE_FILE)
            except: pass

        # النتيجة النهائية
        if cookie_died:
            status_text.error("⛔ Process stopped. Please update your cookie.")
        elif success_count > 0:
            status_text.success("✅ All Done! Zipping files...")
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

if check_password():
    main_app()
