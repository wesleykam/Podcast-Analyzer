import hashlib
import json
from typing import Any, Dict, Tuple, Optional

from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from flask_caching import Cache

from transcript_processor import TranscriptProcessor
from transcript_scraper import TranscriptScraper


# -----------------
# Config
# -----------------
def create_app() -> Flask:
    app = Flask(__name__)

    # Configure CORS restrictions to allow only specific origins
    ALLOWED_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://whimsical-cobbler-80f1b3.netlify.app",
    ]

    CORS(
        app,
        resources={
            r"/*": {
                "origins": ALLOWED_ORIGINS,
                "methods": ["GET", "POST", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                # only turn this on if you need cookies:
                # "supports_credentials": True,
            }
        },
    )

    transcript_processor = TranscriptProcessor()
    scraper = TranscriptScraper(strip_timestamps=True)

    # Start simple (per-process memory). For production, switch to Redis below.
    app.config.update(
        CACHE_TYPE="SimpleCache",
        CACHE_DEFAULT_TIMEOUT=60 * 60,  # 1 hour TTL
        # Redis example:
        # CACHE_TYPE="RedisCache",
        # CACHE_REDIS_URL=os.getenv("CACHE_REDIS_URL", "redis://localhost:6379/0"),
    )

    cache = Cache(app)

    # TTLs (tune as needed)
    RESULT_TTL_SEC = 60 * 60 * 24  # 24h for final analysis
    TRANSCRIPT_TTL_SEC = 60 * 60 * 2  # 2h for URL->transcript (optional)

    # -----------------
    # Helpers
    # -----------------
    def _sha256(s: str) -> str:
        return hashlib.sha256(s.encode("utf-8")).hexdigest()

    def _prompt_hash() -> str:
        prompt = getattr(transcript_processor, "prompt", "")
        return _sha256(prompt)[:12]

    def _model_id() -> str:
        # Adjust if you swap models dynamically
        return "openai:gpt-4o-mini"

    def make_cache_key(route: str, body: Dict[str, Any]) -> str:
        """
        Build a deterministic key from route + JSON body + model + prompt.
        """
        serialized = json.dumps(body, sort_keys=True, ensure_ascii=False)
        body_hash = _sha256(f"{route}::{serialized}")
        return f"analyze:{route}:{_model_id()}:{_prompt_hash()}:{body_hash}"

    def make_transcript_key(url: str) -> str:
        opts = {
            "strip_timestamps": getattr(scraper, "strip_timestamps", True),
            "timeout": getattr(scraper, "timeout", 15),
            "basic_class": getattr(scraper, "basic_selector_class", ""),
            "iframe_sel": getattr(scraper, "iframe_selector", ""),
        }
        opts_hash = _sha256(json.dumps(opts, sort_keys=True, ensure_ascii=False))[:12]
        return f"transcript:{opts_hash}:{_sha256(url)}"

    def cached_compute(
        route: str, body: Dict[str, Any], compute_fn, ttl: Optional[int] = None
    ) -> Tuple[Any, bool]:
        """
        Get from cache or compute + set. Returns (data, hit_bool).
        """
        key = make_cache_key(route, body)
        hit = cache.get(key)
        if hit is not None:
            return hit, True
        data = compute_fn()
        cache.set(
            key, data, timeout=ttl or app.config.get("CACHE_DEFAULT_TIMEOUT", 3600)
        )
        return data, False

    def cached_transcript(url: str) -> Tuple[str, bool]:
        """
        Optional: cache the scraped transcript to avoid repeated Selenium work.
        """
        tkey = make_transcript_key(url)
        hit = cache.get(tkey)
        if hit is not None:
            return hit, True

        driver = scraper.new_driver()
        try:
            driver.get(url)
            text = scraper.extract(driver) or ""
            cache.set(tkey, text, timeout=TRANSCRIPT_TTL_SEC)
            return text, False
        finally:
            try:
                driver.quit()
            except Exception:
                pass

    def normalize_processor_output(raw: Any) -> Dict[str, Any]:
        """
        Ensure we always return a dict (never a JSON string).
        Your processor can return {"error": ...} dict or a JSON string.
        """
        if isinstance(raw, dict):
            return raw
        if isinstance(raw, str):
            try:
                return json.loads(raw)
            except Exception:
                # Fallback: wrap the string
                return {"raw": raw}
        # Unexpected type
        return {"raw": raw}

    # -----------------
    # Analyzers (helpers return dicts only; routes handle jsonify)
    # -----------------
    def analyze_url(url: str) -> Dict[str, Any]:
        transcript, _t_hit = cached_transcript(url)

        if not transcript:
            # Not caching a "not found" final result, but transcript cache will hold empty briefly
            return {
                "error": "Transcript not found on the page. Please check the URL or try another source."
            }

        result = transcript_processor.process_with_openai(transcript)
        return normalize_processor_output(result)

    def analyze_text(text: str) -> Dict[str, Any]:
        result = transcript_processor.process_with_openai(text)
        return normalize_processor_output(result)

    # -----------------
    # Routes
    # -----------------
    @app.post("/analyze-url")
    def analyze_url_route():
        body = request.get_json(silent=True) or {}
        url = (body.get("url") or "").strip()
        if not url:
            return jsonify({"error": "Missing 'url'"}), 400

        try:

            def compute():
                return analyze_url(url)

            data, hit = cached_compute(
                "/analyze-url", {"url": url}, compute, ttl=RESULT_TTL_SEC
            )

            # If processor produced an error, return it with 4xx/5xx
            if isinstance(data, dict) and "error" in data:
                resp = make_response(jsonify(data), 404)
            else:
                resp = make_response(jsonify(data), 200)

            resp.headers["X-Cache"] = "HIT" if hit else "MISS"
            return resp
        except Exception as e:
            return jsonify({"error": str(e) or "Analysis failed"}), 500

    @app.post("/analyze-text")
    def analyze_text_route():
        body = request.get_json(silent=True) or {}
        text = (body.get("text") or "").strip()
        if not text:
            return jsonify({"error": "Missing 'text'"}), 400

        try:
            # Hash text in the key to avoid massive keys
            data, hit = cached_compute(
                "/analyze-text",
                {"text_hash": _sha256(text)},
                lambda: analyze_text(text),
                ttl=RESULT_TTL_SEC,
            )

            if isinstance(data, dict) and "error" in data:
                resp = make_response(jsonify(data), 500)
            else:
                resp = make_response(jsonify(data), 200)

            resp.headers["X-Cache"] = "HIT" if hit else "MISS"
            return resp
        except Exception as e:
            return jsonify({"error": str(e) or "Analysis failed"}), 500

    # -----------------
    # Optional cache ops
    # -----------------
    @app.delete("/cache/clear")
    def clear_cache():
        cache.clear()
        return jsonify({"ok": True})

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
