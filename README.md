# Podcast Transcript Analyzer — Full Stack (Frontend + Backend)

A full-stack tool for analyzing podcast transcripts.

- **Frontend:** React + Vite + TypeScript UI to input a URL or raw text and view results.
- **Backend:** Flask API that (1) scrapes transcripts from a URL (incl. iframes) and (2) analyzes them with OpenAI or Groq to produce a structured JSON report.

---

<details>
<summary><strong>Table of Contents</strong></summary>

- [Monorepo Overview](#monorepo-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Layout](#project-layout)
- [Quickstart (Local Dev)](#quickstart-local-dev)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Running Both Together](#running-both-together)
- [Configuration & Environment](#configuration--environment)
  - [Environment Variables](#environment-variables)
  - [Caching](#caching)
- [Backend API Reference](#backend-api-reference)
  - [Analyze a transcript from a URL](#analyze-a-transcript-from-a-url)
  - [Analyze raw text](#analyze-raw-text)
- [How It Works](#how-it-works)
  - [Scraper (`backend/transcript_scraper.py`)](#scraper-backendtranscript_scraperpy)
  - [Processor (`backend/transcript_processor.py`)](#processor-backendtranscript_processorpy)
  - [Caching (`backend/app.py`)](#caching-backendapppy)
- [Acknowledgments](#acknowledgments)

</details>

---

## Monorepo Overview

- **Goal:** Paste a transcript URL or raw text, click **Analyze**, and see:
  - 3 **Key Takeaways**
  - **Mentioned Organizations & Technologies**
  - 2–3 **Actionable Insights** (each with `header` + `detail`)

The frontend calls the backend’s `/analyze-url` or `/analyze-text` endpoints and renders the returned JSON.

---

## Features

**Backend**
- Robust transcript scraping:
  - Try on-page via `.cfm-transcript-content`
  - Fallback to opening transcript `<iframe src>` in a **new tab** and extracting all `<p>` text
  - Optional removal of timestamps like `[00:12:34]`
- Structured AI output (OpenAI by default; optional Groq)
- Response & transcript **caching** with `X-Cache: HIT|MISS`
- **Deploy-friendly** on Render with pinned Chrome + health check

**Frontend**
- Simple, fast UI (React + Vite + TS)
- URL or Text input; drag-and-drop `.txt`
- Searchable tags for orgs/tech
- Copy/export actions (PDF/Slack placeholders)
- Semantic HTML and accessible controls

---

## Tech Stack

- **Backend:** Flask, Selenium, webdriver-manager, Flask-Caching, OpenAI, Groq
- **Frontend:** React 18, Vite, TypeScript, `react-router-dom`, `axios`, `lucide-react`, plain CSS (tokens/OKLCH)

---

## Project Layout

```

backend/
├─ app.py                     # Flask app factory, routes & caching
├─ transcript\_scraper.py      # Selenium scraper (basic + iframe strategy)
├─ transcript\_processor.py    # OpenAI/Groq clients + prompt + schema
├─ requirements.txt
├─ apt.txt                    # Optional if host supports apt buildpacks (chromium & driver)
├─ render\_build.sh            # Render: download Chrome into persistent layer
├─ render\_start.sh            # Render: export CHROME\_BIN + start gunicorn

# Frontend lives at repo root

src/
├─ App.tsx                    # Routes and redirects
├─ main.tsx                   # App bootstrap
├─ styles/global.css          # Design tokens & global styles
├─ layouts/Layout.tsx
├─ components/...
├─ pages/...
index.html
package.json
vite.config.ts

````

---

## Quickstart (Local Dev)

### Backend Setup

```bash
cd backend

# 1) Python env
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2) Dependencies
pip install -r requirements.txt

# 3) API keys
export OPENAI_API_KEY=sk-...     # PowerShell: $Env:OPENAI_API_KEY="sk-..."
# (Optional) export GROQ_API_KEY=...

# 4) Run (dev)
python app.py                    # http://127.0.0.1:5000

# (Prod-style)
# gunicorn 'app:create_app()' --bind 0.0.0.0:5000
````

> **Chrome/Chromium:** Selenium requires a Chrome/Chromium binary. Locally, `webdriver-manager` downloads a matching ChromeDriver, but you still need Chrome/Chromium installed.

### Frontend Setup

```bash
# from repo root (where package.json lives)
npm install
npm run dev                     # Vite prints local URL (e.g., http://localhost:5173)
```

By default the UI calls `http://localhost:5000`. To change, set `VITE_API_BASE_URL` (see below).

### Running Both Together

* Open **two terminals**: one for `backend`, one for `npm run dev`.
* Ensure CORS is enabled on the backend (it is, by default).

---

## Configuration & Environment

### Environment Variables

**Backend**

* `OPENAI_API_KEY` *(required for default analysis path)*
* `GROQ_API_KEY` *(optional if using Groq)*
* `PORT` *(injected by some hosts; `render_start.sh` uses it)*
* `CHROME_BIN` *(set by `render_start.sh` on Render; local dev usually not needed)*

**Frontend**

* `VITE_API_BASE_URL` *(optional; defaults to `http://localhost:5000`)*

Create a `.env` (or `.env.local`) in the frontend root:

```env
VITE_API_BASE_URL=http://localhost:5000
```

And in your API calls (e.g., `InputPanel.tsx`):

```ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:5000';
```

### Caching

Backend default: `SimpleCache` (per-process, in-memory).

* `RESULT_TTL_SEC = 24h` (final analysis)
* `TRANSCRIPT_TTL_SEC = 2h` (URL → transcript text)

For production/multi-instance, switch to **Redis** (see comments in `app.py`).

---

## Backend API Reference

### Analyze a transcript from a URL

`POST /analyze-url`

**Body**

```json
{ "url": "https://example.com/some-podcast-episode" }
```

**Success (200)**

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

---

### Analyze raw text

`POST /analyze-text`

**Body**

```json
{ "text": "Full transcript goes here..." }
```

*Response shape and errors are the same as `/analyze-url`.*

---

## How It Works

### Scraper (`backend/transcript_scraper.py`)

* **Basic mode:** collect text from elements with `.cfm-transcript-content`.
* **Iframe mode:** find a likely transcript `<iframe>`, open its `src` in a **new tab**, aggregate all `<p>` text, then close and return.
* **Cleaning:** remove timestamps like `[00:12:34]` and collapse whitespace.

### Processor (`backend/transcript_processor.py`)

Structured schema enforced via Pydantic:

```python
class ActionableInsight(BaseModel):
    header: str
    detail: str

class TranscriptAnalysis(BaseModel):
    summary: list[str]
    mentioned_organizations: list[str]
    actionable_insights: list[ActionableInsight]
```

* Default path: **OpenAI** (e.g., `gpt-4o-mini`) with strict JSON parsing.
* Optional **Groq** path included.

### Caching (`backend/app.py`)

* **Final analysis cache key:** route + request body + model id + prompt hash.
* **Transcript cache key:** URL + scraper options (so selector changes create a new namespace).
* Responses normalized to `dict`.

---

## Acknowledgments

* Selenium + webdriver-manager
* Flask-Caching
* OpenAI / Groq SDKs
* `lucide-react` icons
