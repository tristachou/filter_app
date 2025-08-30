import requests
import json
import threading
import time

BASE_URL = "http://ec2-3-107-52-165.ap-southeast-2.compute.amazonaws.com"
LOGIN_URL = f"{BASE_URL}/api/auth/token"
PROCESS_URL = f"{BASE_URL}/api/process"


MEDIA_ID = "fd9b29d1-cfef-41a6-9186-4ed17441ae6b"  
FILTER_ID = "a250efc4-50d4-4ede-b0f1-17e73007be65"   
NUM_THREADS = 10 
REQUESTS_PER_THREAD = 50  

def login_and_get_token(username, password):
    
    try:
        response = requests.post(LOGIN_URL, data={"username": username, "password": password})
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"login fail: {e}")
        return None

def process_media_request(token, thread_id):
   
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
        print(f"thread {thread_id} - status code: {response.status_code}")
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"thread {thread_id} - request fail: {e}")
       

def load_test_thread(token, thread_id):
    
    for i in range(REQUESTS_PER_THREAD):
        process_media_request(token, thread_id)
       

def run_load_test():
    
    print("--- start loading test ---")
    
    
    token = login_and_get_token("user2", "fake_password_2")
    if not token:
        print("login fail")
        return
        
    print("login success, start loading test")
    
    
    threads = []
    for i in range(NUM_THREADS):
        thread = threading.Thread(target=load_test_thread, args=(token, i))
        threads.append(thread)
        thread.start()
    
    
    for thread in threads:
        thread.join()
    
        
    print("--- finish ---")

if __name__ == "__main__":
    run_load_test()