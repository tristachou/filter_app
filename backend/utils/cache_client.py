import os
import json
from pymemcache.client.base import Client
from pymemcache.exceptions import MemcacheError
from typing import Optional, Any

# --- Memcached Client Setup ---

# Get the Memcached endpoint from an environment variable
# Example: 'your-elasticache-endpoint.xxxxxx.cfg.aps1.cache.amazonaws.com:11211'
MEMCACHED_ENDPOINT = os.getenv("MEMCACHED_ENDPOINT")

memcache_client = None
if MEMCACHED_ENDPOINT:
    print(f"Connecting to Memcached at: {MEMCACHED_ENDPOINT}")
    # Splitting host and port
    try:
        host, port = MEMCACHED_ENDPOINT.split(':')
        memcache_client = Client((host, int(port)), connect_timeout=5, timeout=5)
        # Verify connection by getting server version
        memcache_client.version()
        print("Successfully connected to Memcached.")
    except (MemcacheError, ConnectionRefusedError, TimeoutError, ValueError) as e:
        print(f"\033[91mWarning: Could not connect to Memcached at {MEMCACHED_ENDPOINT}. Caching will be disabled. Error: {e}\033[0m")
        memcache_client = None
else:
    print("\033[93mWarning: MEMCACHED_ENDPOINT environment variable not set. Caching will be disabled.\033[0m")

def set_to_cache(key: str, value: Any, expire: int = 60):
    """
    Serializes a Python object to JSON and stores it in the cache.
    
    :param key: The key to store the data under.
    :param value: The Python object to store (must be JSON serializable).
    :param expire: Expiration time in seconds. Defaults to 60.
    """
    if not memcache_client:
        return

    try:
        # Serialize the Python dict/list to a JSON string, then encode to bytes
        serialized_value = json.dumps(value).encode('utf-8')
        memcache_client.set(key, serialized_value, expire=expire)
    except (TypeError, MemcacheError) as e:
        # TypeError for non-serializable objects, MemcacheError for connection issues
        print(f"\033[91mError setting cache for key '{key}': {e}\033[0m")

def get_from_cache(key: str) -> Optional[Any]:
    """
    Retrieves an item from the cache and deserializes it from JSON.
    
    :param key: The key of the item to retrieve.
    :return: The deserialized Python object, or None if not found or on error.
    """
    if not memcache_client:
        return None

    try:
        cached_value = memcache_client.get(key)
        if cached_value:
            # Decode bytes to a JSON string, then parse to a Python object
            return json.loads(cached_value.decode('utf-8'))
        return None
    except (json.JSONDecodeError, MemcacheError) as e:
        print(f"\033[91mError getting or decoding cache for key '{key}': {e}\033[0m")
        return None
