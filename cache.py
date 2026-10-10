from flask_caching import Cache

cache = Cache()


def init_cache(app):
    cache_type = app.config.get("CACHE_TYPE", "redis")
    config = {"CACHE_TYPE": cache_type, "CACHE_REDIS_URL": "redis://localhost:6379/0", "CACHE_DEFAULT_TIMEOUT": 300, "CACHE_KEY_PREFIX": "placement_"}
    cache.init_app(app, config=config)
