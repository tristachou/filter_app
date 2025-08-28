import requests
import threading
import time
import os

# --- Configuration ---
API_URL = "http://localhost:8000/process/" # Change if your endpoint is different
JWT_TOKEN = "your_jwt_token_here" # <--- IMPORTANT: Get this after logging in
VIDEO_FILE_PATH = "path/to/your/large_video.mp4" # <--- IMPORTANT: Path to your test video
LUT_NAME = "default_lut.cube" # Or any other LUT file name you have
CONCURRENT_REQUESTS = 4 # Number of simultaneous uploads. Adjust based on your machine's cores.
TEST_DURATION_SECONDS = 300 # 5 minutes

# --- Check if the video file exists ---
if not os.path.exists(VIDEO_FILE_PATH):
    print(f"❌ Error: Video file not found at '{VIDEO_FILE_PATH}'")
    exit()

def send_request(n):
    """Function to send a single file upload and processing request."""
    print(f"Thread {n}: Starting request...")
    try:
        with open(VIDEO_FILE_PATH, 'rb') as f:
            files = {'file': (os.path.basename(VIDEO_FILE_PATH), f)}
            headers = {'Authorization': f'Bearer {JWT_TOKEN}'}
            data = {'lut_filename': LUT_NAME}
            
            response = requests.post(API_URL, files=files, headers=headers, data=data, timeout=360) # 6 min timeout
            
            if response.status_code == 200:
                print(f"✅ Thread {n}: Request successful (Status: {response.status_code})")
            else:
                print(f"⚠️ Thread {n}: Request failed (Status: {response.status_code}, Response: {response.text})")

    except requests.exceptions.RequestException as e:
        print(f"❌ Thread {n}: An error occurred: {e}")

# --- Main test logic ---
print(f"🚀 Starting load test for {TEST_DURATION_SECONDS / 60} minutes...")
print(f"Simulating {CONCURRENT_REQUESTS} concurrent users.")

end_time = time.time() + TEST_DURATION_SECONDS
threads = []

while time.time() < end_time:
    # Clean up finished threads
    threads = [t for t in threads if t.is_alive()]
    
    # Start new threads if we have capacity
    if len(threads) < CONCURRENT_REQUESTS:
        thread_num = len(threads) + 1
        thread = threading.Thread(target=send_request, args=(thread_num,))
        thread.start()
        threads.append(thread)
    
    time.sleep(1) # Wait a second before checking to start a new thread

# Wait for all running threads to complete
for t in threads:
    t.join()

print("✅ Load test finished.")