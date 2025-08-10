# Podcast Transcript Analyzer — Frontend

A React + Vite + TypeScript UI for submitting a podcast transcript **URL or raw text** and viewing:
- 3 **Key Takeaways**
- **Mentioned Organizations & Technologies**
- 2–3 **Actionable Insights** (each with `header` + `detail`)

The app calls the backend’s `/analyze-url` or `/analyze-text` endpoints and renders the returned JSON.

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Scripts](#scripts)
- [Troubleshooting](#troubleshooting)
- [Acknowledgments](#acknowledgments)

## Features
- Fast Vite dev server with TypeScript
- URL or text input (drag-and-drop `.txt` supported)
- Displays summary, organizations/tech, and actionable insights
- Copy/export action placeholders (PDF/Slack)
- Semantic HTML and accessible controls

## Tech Stack
- **React 18**, **Vite**, **TypeScript**
- `react-router-dom`, `axios`, `lucide-react`
- Plain CSS (design tokens/OKLCH)

## Getting Started
```bash
# In the frontend/ directory
npm install
npm run dev      # e.g., http://localhost:5173
````

## Configuration

Set the backend base URL via Vite env:

Create `.env` (or `.env.local`) in `frontend/`:

```env
VITE_API_BASE_URL=http://localhost:5000
```

Use it in code (already wired in components):

```ts
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:5000';
```

## Project Structure

```
src/
├─ App.tsx                 # Routes and redirects
├─ main.tsx                # App bootstrap
├─ styles/global.css       # Design tokens & global styles
├─ layouts/Layout.tsx
├─ components/...
├─ pages/...
index.html
package.json
vite.config.ts
```

## Scripts

```bash
npm run dev       # Start dev server
npm run build     # Production build
npm run preview   # Preview production build
```

## Troubleshooting

* **CORS errors:** Ensure the backend enables CORS and that `VITE_API_BASE_URL` points to the correct backend origin.
* **Network failures:** Check that the backend is running (default: `http://localhost:5000`).

## Acknowledgments

* `lucide-react` for icons

