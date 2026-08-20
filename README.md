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

## Optional: enable "Connect Gmail"

This lets you search your inbox and load a real thread straight into the summarizer, instead of
pasting text. It's optional — the app works fine without it. Setting it up requires creating your
own OAuth credentials in Google Cloud Console (Google requires this per-app; there's no shared key
Claude or anyone else can hand you).

1. Go to [console.cloud.google.com](https://console.cloud.google.com) and create a project (or use an existing one).
2. **Enable the Gmail API**: APIs & Services → Library → search "Gmail API" → Enable.
3. **Configure the OAuth consent screen**: APIs & Services → OAuth consent screen.
   - User type: External (unless you have a Google Workspace org).
   - Fill in the required app name/support email fields.
   - Scopes: add `https://www.googleapis.com/auth/gmail.readonly`.
   - Test users: add your own Gmail address (required while the app is in "Testing" mode — this is fine for personal use, no need to publish/verify it).
4. **Create credentials**: APIs & Services → Credentials → Create Credentials → OAuth client ID.
   - Application type: **Web application**.
   - Authorized redirect URIs: add your deployed app's exact URL, e.g.
     `https://relay-agent-summarizer-xxxxxxxx.streamlit.app`
     (no trailing slash, must match exactly what's in your browser's address bar).
5. Copy the **Client ID** and **Client Secret** it gives you.
6. Add all three values to Streamlit secrets (locally in `secrets.toml`, or in Streamlit Cloud → Settings → Secrets):
   ```toml
   GOOGLE_CLIENT_ID = "xxxxx.apps.googleusercontent.com"
   GOOGLE_CLIENT_SECRET = "xxxxx"
   GOOGLE_REDIRECT_URI = "https://relay-agent-summarizer-xxxxxxxx.streamlit.app"
   ```
7. Reload the app. Under **Source → Email thread**, a "Connect Gmail" option will now appear next
   to "Paste or upload."

Note: since the app stays in Google's "Testing" publishing status, only the test users you added
in step 3 can authorize it — that's expected and fine for a personal tool. Access tokens are kept
only in that browser session's memory, never written to disk or committed anywhere.

## Files

- `app.py` — the Streamlit app
- `requirements.txt` — Python dependencies (Gemini SDK + optional Gmail OAuth libs)
- `.streamlit/config.toml` — theme (indigo/void background, coral/violet/cyan accents)
- `.streamlit/secrets.toml.example` — template for your local secrets file (copy → rename → fill in)
- `.gitignore` — keeps `secrets.toml`, venvs, and editor files out of the repo
- `LICENSE` — MIT
