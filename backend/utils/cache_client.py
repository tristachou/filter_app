import os
import json
from pymemcache.client.base import Client
from pymemcache.exceptions import MemcacheError
from typing import Optional, Any

# --- Lazy-Initialized Memcached Client ---

# This will hold the client instance once it's connected.
_memcache_client: Optional[Client] = None
_memcache_client_initialized: bool = False

def _get_client() -> Optional[Client]:
    """
    Lazily initializes and returns the Memcached client.
    The connection is only attempted on the first call.
    """
    global _memcache_client, _memcache_client_initialized

    # If we've already tried to initialize, don't try again.
    if _memcache_client_initialized:
        return _memcache_client

    MEMCACHED_ENDPOINT = os.getenv("MEMCACHED_ENDPOINT")
    
    if MEMCACHED_ENDPOINT:
        print(f"Attempting to connect to Memcached at: {MEMCACHED_ENDPOINT}")
        try:
            host, port = MEMCACHED_ENDPOINT.split(':')
            client = Client((host, int(port)), connect_timeout=2, timeout=2)
            # Verify connection by getting server version. This is the crucial part.
            client.version()
            print("Successfully connected to Memcached.")
            _memcache_client = client
        except (MemcacheError, ConnectionRefusedError, TimeoutError, ValueError, OSError) as e:
            print(f"\033[91mWarning: Could not connect to Memcached. Caching will be disabled. Error: {e}\033[0m")
            _memcache_client = None
    else:
        print("\033[93mWarning: MEMCACHED_ENDPOINT environment variable not set. Caching will be disabled.\033[0m")

    _memcache_client_initialized = True
    return _memcache_client

def set_to_cache(key: str, value: Any, expire: int = 60):
    """
    Serializes a Python object to JSON and stores it in the cache.
    
    :param key: The key to store the data under.
    :param value: The Python object to store (must be JSON serializable).
    :param expire: Expiration time in seconds. Defaults to 60.
    """
    client = _get_client()
    if not client:
        return

    try:
        # Serialize the Python dict/list to a JSON string, then encode to bytes
        serialized_value = json.dumps(value).encode('utf-8')
        client.set(key, serialized_value, expire=expire)
    except (TypeError, MemcacheError) as e:
        # TypeError for non-serializable objects, MemcacheError for connection issues
        print(f"\033[91mError setting cache for key '{key}': {e}\033[0m")

def get_from_cache(key: str) -> Optional[Any]:
    """
    Retrieves an item from the cache and deserializes it from JSON.
    
    :param key: The key of the item to retrieve.
    :return: The deserialized Python object, or None if not found or on error.
    """
    client = _get_client()
    if not client:
        return None

    try:
        cached_value = client.get(key)
        if cached_value:
            # Decode bytes to a JSON string, then parse to a Python object
            return json.loads(cached_value.decode('utf-8'))
        return None
    except (json.JSONDecodeError, MemcacheError) as e:
        print(f"\033[91mError getting or decoding cache for key '{key}': {e}\033[0m")
        return None
