# Relay — Agent Trace Summarizer

Paste in an email thread, meeting transcript, PDF, or screenshot, and watch the agent trace
through parsing → extraction → structuring. Get back a summary, action items (owner, due date,
priority), and key decisions — powered by Gemini.

The Gemini API key lives in **Streamlit secrets**, not in a text box on the page — it's never
typed into the app's UI or stored in the repo.

## Run locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Add your key. Copy the example secrets file and fill it in:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
   Then edit `.streamlit/secrets.toml`:
   ```toml
   GEMINI_API_KEY = "your-key-here"
   ```
   This file is gitignored — it will never get committed.

3. Run it:
   ```bash
   streamlit run app.py
   ```

## Deploy on Streamlit Community Cloud (free)

1. **Push this folder to GitHub** — `secrets.toml` will be skipped automatically thanks to `.gitignore`.
   ```bash
   git init
   git add .
   git commit -m "Relay agent summarizer"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git push -u origin main
   ```

2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.

3. Click **New app**, pick your repo/branch, and set the main file path to:
   ```
   app.py
   ```

4. Before (or right after) deploying, go to **Settings → Secrets** in the app dashboard and add:
   ```toml
   GEMINI_API_KEY = "your-key-here"
   ```

5. Click **Deploy**. The app restarts automatically once the secret is saved, and the
   "connect Gemini" setup panel disappears — the app just shows "Connected to Gemini."

## Get a Gemini API key

Create one for free at [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

## Files

- `app.py` — the Streamlit app
- `requirements.txt` — Python dependencies
- `.streamlit/config.toml` — theme (indigo/void background, coral/violet/cyan accents)
- `.streamlit/secrets.toml.example` — template for your local secrets file (copy → rename → fill in)
- `.gitignore` — keeps `secrets.toml`, venvs, and editor files out of the repo
- `LICENSE` — MIT
