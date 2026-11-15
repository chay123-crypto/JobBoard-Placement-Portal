import os

from flask import request
from flask_caching import Cache
from flask_login import current_user

cache = Cache()


def user_cache_key():
    return f"{request.endpoint}:{request.full_path}:{current_user.get_id()}"


def init_cache(app):
    cache_type = app.config.get("CACHE_TYPE") or "SimpleCache"
    config = {
        "CACHE_TYPE": cache_type,
        "CACHE_DEFAULT_TIMEOUT": 300,
        "CACHE_KEY_PREFIX": "placement_",
    }
    if cache_type.lower() in {"redis", "rediscache"}:
        redis_url = app.config.get("CACHE_REDIS_URL") or app.config.get("REDIS_URL") or os.environ.get("REDIS_URL")
        if not redis_url:
            raise RuntimeError("Redis caching requires CACHE_REDIS_URL or REDIS_URL")
        config["CACHE_REDIS_URL"] = redis_url
    cache.init_app(app, config=config)
