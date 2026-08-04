# Relay — Agent Trace Summarizer

Paste in an email thread or meeting transcript, watch the agent trace through
parsing → extraction → structuring, and get back a summary, action items
(owner, due date, priority), and key decisions — powered by Gemini.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL Streamlit prints (usually `http://localhost:8501`)
and paste in your Gemini API key in the app itself.

## Deploy on Streamlit Community Cloud (free)

1. **Push this folder to GitHub.**
   ```bash
   git init
   git add .
   git commit -m "Relay agent summarizer"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git push -u origin main
   ```

2. **Go to** [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.

3. Click **New app**, pick your repo/branch, and set the main file path to:
   ```
   app.py
   ```

4. Click **Deploy**. Streamlit builds the app from `requirements.txt` automatically.

5. Once it's live, open the app URL and paste your Gemini API key into the
   **Configure** panel — the key is only used for that browser session's
   requests to Google's API and isn't stored by the app or the repo.

### Optional: pre-fill the key via Streamlit secrets instead of typing it every time

In the Streamlit Cloud dashboard for your app, go to **Settings → Secrets** and add:

```toml
GEMINI_API_KEY = "your-key-here"
```

Then in `app.py`, you could default the text input to
`st.secrets.get("GEMINI_API_KEY", "")` so it's pre-filled but still editable.
This keeps the key out of your GitHub repo entirely — never commit an API key
directly into the code.

## Get a Gemini API key

Create one for free at [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

## Files

- `app.py` — the Streamlit app
- `requirements.txt` — Python dependencies
- `.streamlit/config.toml` — dark theme (ink background, amber accent, teal highlights)
