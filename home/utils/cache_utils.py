# utils/cache_utils.py
from django.core.cache import cache
from functools import wraps
import hashlib
import json

def cache_key_generator(*args, **kwargs):
    key_parts = [str(arg) for arg in args]
    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()

def cache_response(timeout=300):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            cache_key = f"view_cache:{cache_key_generator(*args, **kwargs)}"
            response = cache.get(cache_key)
            
            if response is None:
                response = view_func(*args, **kwargs)
                cache.set(cache_key, response, timeout)
            
            return response
        return wrapped_view
    return decorator