import requests
import json
import threading
import time

# --- 設定 API 資訊 ---
BASE_URL = "http://ec2-3-107-52-165.ap-southeast-2.compute.amazonaws.com"
LOGIN_URL = f"{BASE_URL}/api/auth/token"
PROCESS_URL = f"{BASE_URL}/api/process"

# --- 設定測試參數 ---
# 這兩個 ID 必須是你資料庫中實際存在的媒體和濾鏡 ID。
MEDIA_ID = "fd9b29d1-cfef-41a6-9186-4ed17441ae6b"  # 範例 media_id
FILTER_ID = "a250efc4-50d4-4ede-b0f1-17e73007be65"   # 範例 filter_id
NUM_THREADS = 10  # 同時模擬 10 個使用者
REQUESTS_PER_THREAD = 50  # 每個使用者發送 50 個請求

def login_and_get_token(username, password):
    """
    登入並取得 JWT 權杖。
    """
    try:
        response = requests.post(LOGIN_URL, data={"username": username, "password": password})
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"登入失敗: {e}")
        return None

def process_media_request(token, thread_id):
    """
    發送單一處理媒體的請求。
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "media_id": MEDIA_ID,
        "filter_id": FILTER_ID
    }
    
    try:
        response = requests.post(PROCESS_URL, headers=headers, data=json.dumps(payload))
        print(f"執行緒 {thread_id} - 回應狀態碼: {response.status_code}")
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"執行緒 {thread_id} - 請求失敗: {e}")

def load_test_thread(token, thread_id):
    """
    單一執行緒，發送多個請求。
    """
    for i in range(REQUESTS_PER_THREAD):
        process_media_request(token, thread_id)
        # 為了避免短時間內發送太多請求，可以加入延遲
        # time.sleep(0.1)

def run_load_test():
    """
    主函式，管理所有測試執行緒。
    """
    print("--- 開始負載測試 ---")
    
    # 1. 登入以取得權杖
    token = login_and_get_token("user2", "fake_password_2")
    if not token:
        print("無法取得權杖，請檢查登入資訊和 API 服務。")
        return
        
    print("成功登入，開始發送請求...")
    
    # 2. 建立並啟動多個執行緒
    threads = []
    for i in range(NUM_THREADS):
        thread = threading.Thread(target=load_test_thread, args=(token, i))
        threads.append(thread)
        thread.start()
    
    # 3. 等待所有執行緒完成
    for thread in threads:
        thread.join()
    
        
    print("--- 負載測試完成 ---")

if __name__ == "__main__":
    run_load_test()