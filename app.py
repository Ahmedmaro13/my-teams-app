import streamlit as st
import yt_dlp
import os
import shutil
import time

st.set_page_config(page_title="Emergency Debugger 🚑", page_icon="🚨")

def main_app():
    st.title("🚨 Emergency Debugger (النسخة الخام)")
    st.warning("هذه النسخة مخصصة لكشف الأخطاء. لا توجد فلاتر جودة.")

    # 1. إدخال الكوكيز
    cookie = st.text_input("🍪 Cookie (تأكد أنها جديدة!)")
    
    # 2. إدخال الروابط
    urls = st.text_area("🔗 URLs")

    if st.button("Try Download (Raw Mode) 🚀"):
        if not cookie or not urls:
            st.error("أدخل البيانات أولاً!")
            return

        # تنظيف مجلد التحميل
        if os.path.exists("debug_downloads"):
            shutil.rmtree("debug_downloads")
        os.makedirs("debug_downloads")

        url_list = urls.strip().split('\n')
        
        for i, url in enumerate(url_list):
            if not url.strip(): continue
            
            st.write(f"--- \n **🔎 Testing Link {i+1}...**")
            
            # إعدادات بسيطة جداً جداً لكشف الخطأ
            ydl_opts = {
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                    'Cookie': cookie,
                    'Referer': 'https://aastpg.sharepoint.com/',
                },
                'outtmpl': f'debug_downloads/{i+1}_%(title)s.%(ext)s',
                'format': 'best', # هات أي حاجة قدامك
                'verbose': True,  # اظهر كل التفاصيل
                'ignoreerrors': False, # لو حصل خطأ، اصرخ وماتسكتش
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    st.success(f"✅ Downloaded: {info.get('title', 'Unknown')}")
                    st.write(f"📁 Ext: {info.get('ext')} | 📏 Resolution: {info.get('resolution')}")
            
            except Exception as e:
                # اطبع الخطأ باللون الأحمر العريض
                st.error(f"❌ CRITICAL ERROR:\n{e}")
                st.code(str(e)) # عرض الخطأ ككود للنسخ

        # محاولة الضغط (حتى لو فشل التحميل)
        if os.listdir("debug_downloads"):
            shutil.make_archive("Debug_Bundle", 'zip', "debug_downloads")
            with open("Debug_Bundle.zip", "rb") as f:
                st.download_button("📥 Download Result", f, "Debug.zip")
        else:
            st.warning("المجلد فارغ! لم يتم تحميل أي شيء.")

if __name__ == "__main__":
    main_app()
