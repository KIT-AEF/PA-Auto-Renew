import os
import sys
import json
import requests
import time
from bs4 import BeautifulSoup

# قراءة الحسابات من المتغير المجمع
ACCOUNTS_JSON = os.environ.get('ACCOUNTS_JSON')
PASSWORD = os.environ.get('PA_PASSWORD')

if not ACCOUNTS_JSON or not PASSWORD:
    print("❌ Error: ACCOUNTS_JSON and PA_PASSWORD must be set")
    sys.exit(1)

accounts = json.loads(ACCOUNTS_JSON)

def renew_account(username, password):
    LOGIN_URL = "https://www.pythonanywhere.com/login/"
    DASHBOARD_URL = f"https://www.pythonanywhere.com/user/{username}/webapps/"
    
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    
    try:
        print(f"🔐 Logging in as {username}...")
        login_page = session.get(LOGIN_URL, timeout=10)
        soup = BeautifulSoup(login_page.content, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
        
        payload = {'csrfmiddlewaretoken': csrf_token, 'auth-username': username, 'auth-password': password, 'login_view-current_step': 'auth'}
        
        response = session.post(LOGIN_URL, data=payload, headers={'Referer': LOGIN_URL}, timeout=10, allow_redirects=True)
        
        if "Log out" not in response.text:
            print(f"❌ Login failed for {username}")
            return False
            
        print(f"✅ Login successful for {username}")
        dashboard = session.get(DASHBOARD_URL, timeout=10)
        soup = BeautifulSoup(dashboard.content, 'html.parser')
        
        forms = soup.find_all('form', action=True)
        extend_action = next((form.get('action') for form in forms if "/extend" in form.get('action', '').lower()), None)
        
        if not extend_action:
            print(f"ℹ️ No extend button found for {username}")
            return True
        
        dashboard_csrf = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
        extend_url = f"https://www.pythonanywhere.com{extend_action}"
        
        result = session.post(extend_url, data={'csrfmiddlewaretoken': dashboard_csrf}, headers={'Referer': DASHBOARD_URL}, timeout=10)
        
        if result.status_code == 200 and "webapps" in result.url.lower():
            print(f"✅ Web app for {username} extended successfully!")
            return True
        return False
            
    except Exception as e:
        print(f"❌ Error processing {username}: {e}")
        return False

if __name__ == "__main__":
    for user in accounts:
        renew_account(user, PASSWORD)
        time.sleep(10) # راحة بين الحسابات
    sys.exit(0)
