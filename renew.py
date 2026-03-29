import os
import json
import requests
import time
from bs4 import BeautifulSoup

# قراءة البيانات من متغيرات البيئة (GitHub Secrets)
accounts_json = os.environ.get('ACCOUNTS_JSON')
password = os.environ.get('PA_PASSWORD')

if not accounts_json or not password:
    print("❌ خطأ: تأكد من إعداد ACCOUNTS_JSON و PA_PASSWORD في الـ GitHub Secrets")
    exit(1)

accounts = json.loads(accounts_json)

def renew_account(username, password):
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
    
    try:
        # 1. الدخول لصفحة تسجيل الدخول
        login_url = "https://www.pythonanywhere.com/login/"
        response = session.get(login_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
        
        # 2. إرسال بيانات الدخول
        payload = {
            'csrfmiddlewaretoken': csrf_token,
            'auth-username': username,
            'auth-password': password,
            'login_view-current_step': 'auth'
        }
        
        res = session.post(login_url, data=payload, headers={'Referer': login_url})
        
        # التحقق من نجاح الدخول
        if "Log out" not in res.text and "logout" not in res.text.lower():
            print(f"❌ فشل تسجيل الدخول للحساب: {username}")
            return
            
        print(f"✅ تم تسجيل الدخول لـ {username}")
        
        # 3. الذهاب لصفحة الويب أبس
        dashboard_url = f"https://www.pythonanywhere.com/user/{username}/webapps/"
        dashboard = session.get(dashboard_url)
        soup = BeautifulSoup(dashboard.content, 'html.parser')
        
        # 4. البحث عن زر التمديد
        extend_form = soup.find('form', action=lambda x: x and '/extend' in x)
        
        if not extend_form:
            print(f"ℹ️ الحساب {username} لا يحتاج تمديد حالياً.")
            return
            
        # 5. تنفيذ التمديد
        extend_url = f"https://www.pythonanywhere.com{extend_form['action']}"
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
        
        result = session.post(extend_url, data={'csrfmiddlewaretoken': csrf_token}, headers={'Referer': dashboard_url})
        
        if result.status_code == 200:
            print(f"🎉 تم تمديد الحساب {username} بنجاح!")
        else:
            print(f"❌ حدث خطأ أثناء تمديد {username}")
            
    except Exception as e:
        print(f"⚠️ خطأ غير متوقع أثناء معالجة {username}: {e}")

if __name__ == "__main__":
    print(f"🚀 بدء عملية التمديد لـ {len(accounts)} حساب...")
    for user in accounts:
        renew_account(user, password)
        time.sleep(10) # تأخير 10 ثوانٍ بين كل حساب
    print("🏁 انتهت المهمة.")
