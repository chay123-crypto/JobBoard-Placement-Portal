from flask import Flask

from backend.cache import cache, init_cache


def test_cache_defaults_to_simple_cache_and_can_be_cleared():
    app = Flask(__name__)
    init_cache(app)

    with app.app_context():
        assert cache.cache.__class__.__name__ == "SimpleCache"
        cache.set("resume-upload-probe", "value")
        cache.clear()
        assert cache.get("resume-upload-probe") is None


def test_redis_cache_requires_a_configured_url():
    app = Flask(__name__)
    app.config["CACHE_TYPE"] = "RedisCache"

    try:
        init_cache(app)
    except RuntimeError as exc:
        assert "CACHE_REDIS_URL or REDIS_URL" in str(exc)
    else:
        raise AssertionError("Redis cache was initialized without a Redis URL")
