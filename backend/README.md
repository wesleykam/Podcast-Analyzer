# Podcast Transcript Analyzer — Backend (Flask)

A Flask API that:
1) scrapes podcast transcripts from a URL (including iframes), and  
2) analyzes the transcript with OpenAI (or Groq) to return a structured JSON report.

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Requirements](#requirements)
- [Quickstart](#quickstart)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Caching](#caching)
- [API Reference](#api-reference)
  - [/analyze-url](#post-analyze-url)
  - [/analyze-text](#post-analyze-text)
- [How It Works](#how-it-works)
  - [Scraper](#scraper)
  - [Processor](#processor)
  - [Caching Details](#caching-details)
- [Deployment Notes](#deployment-notes)
- [Acknowledgments](#acknowledgments)

## Features
- Robust transcript scraping:
  - On-page via `.cfm-transcript-content`
  - Fallback to opening transcript `<iframe src>` in a **new tab** and aggregating `<p>` text
  - Optional removal of timestamps like `[00:12:34]`
- Structured AI output (OpenAI by default; optional Groq)
- Response & transcript **caching** with `X-Cache: HIT|MISS`
- Render-friendly scripts for pinned Chrome + health check

## Tech Stack
- **Flask**, **Selenium**, `webdriver-manager`, **Flask-Caching**
- **OpenAI**, **Groq**

## Requirements
- **Python** 3.10+
- **Chrome/Chromium** installed on the host  
  Selenium uses a matching ChromeDriver via `webdriver-manager`. In containers, set `CHROME_BIN` if needed.

## Quickstart
```bash
cd backend

# 1) Python env
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate

# 2) Dependencies
pip install -r requirements.txt

# 3) Environment
export OPENAI_API_KEY=sk-...        # PowerShell: $Env:OPENAI_API_KEY="sk-..."
# (Optional) export GROQ_API_KEY=...
export FLASK_ENV=development

# 4) Run (dev)
python app.py                       # http://127.0.0.1:5000

# (Prod-style)
# gunicorn 'app:create_app()' --bind 0.0.0.0:5000
````

## Configuration

### Environment Variables

* `OPENAI_API_KEY` *(required for default analysis path)*
* `GROQ_API_KEY` *(optional if using Groq)*
* `FLASK_ENV` *(use `development` for local dev; enables permissive CORS)*

### Caching

Default: `SimpleCache` (in-process). Tunables (defined in `app.py`):

* `RESULT_TTL_SEC = 24h` — final analysis
* `TRANSCRIPT_TTL_SEC = 2h` — URL → transcript text

For multi-instance production, switch to **Redis** (`CACHE_TYPE="RedisCache"`, `CACHE_REDIS_URL=...`).

## API Reference

### POST `/analyze-url`

**Body**

```json
{ "url": "https://thisweekhealth.com/captivate-podcast/newsday-prior-auth-ai-and-breaking-down-geographic-barriers-with-colin-banas/" }
```

**200 Response**

```json
{
  "summary": ["Takeaway 1", "Takeaway 2", "Takeaway 3"],
  "mentioned_organizations": ["Epic", "Mayo Clinic", "HL7"],
  "actionable_insights": [
    { "header": "Streamline Prior Auth", "detail": "Apply automation to reduce friction and delays." },
    { "header": "Clinician-In-The-Loop AI", "detail": "Create clear governance and feedback pathways." }
  ]
}
```

**Errors**

* `400` — missing/invalid body
* `404` — transcript could not be found/scraped
* `500` — unexpected failure

**Headers**

* `X-Cache: HIT|MISS` — whether the **final analysis** was served from cache

### POST `/analyze-text`

**Body**

```json
{ "text": "Full transcript goes here..." }
```

Response shape and errors are the same as `/analyze-url`.

> Optional utility endpoints (if enabled):
>
> * `GET /health` → `{ "ok": true }`
> * `POST /cache/clear` → clears caches

## How It Works

### Scraper

* **Basic mode:** collect text from `.cfm-transcript-content`.
* **Iframe mode:** locate a likely transcript `<iframe>`, open its `src` in a **new tab**, aggregate all `<p>` text, then close and return.
* **Cleaning:** remove timestamps like `[00:12:34]`, collapse whitespace.

### Processor

Pydantic-enforced schema:

```python
class ActionableInsight(BaseModel):
    header: str
    detail: str

class TranscriptAnalysis(BaseModel):
    summary: list[str]
    mentioned_organizations: list[str]
    actionable_insights: list[ActionableInsight]
```

* Default path uses **OpenAI** (e.g., `gpt-4o-mini`) with strict JSON parsing.
* **Groq** path available.

### Caching Details

* **Final analysis cache key:** route + request body + model id + prompt hash.
* **Transcript cache key:** URL + scraper options (selector/timestamp flags etc.).
* Responses normalized to `dict`.

## Deployment Notes

* **Render**: included helper scripts:

  * `render_build.sh` — downloads Chrome into a persistent layer
  * `render_start.sh` — exports `CHROME_BIN` and starts `gunicorn`
* If your host supports apt buildpacks, `apt.txt` lists `chromium` and `chromium-driver`.
* Common Chrome flags for containers: `--headless=new --no-sandbox --disable-dev-shm-usage --disable-gpu`.

## Acknowledgments

* Selenium + webdriver-manager
* Flask-Caching
* OpenAI / Groq SDKs
