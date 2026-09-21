# Ask Ahmed — V5

A bilingual Streamlit AI profile for Ahmed Omar.

## Run locally

1. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
2. Add your Gemini API key:

```toml
GEMINI_API_KEY = "your_key_here"
```

3. Install dependencies:

```powershell
py -m pip install -r requirements.txt
```

4. Run:

```powershell
py -m streamlit run app.py
```

## Notes
- The interface supports English and Arabic.
- Sidebar navigation and topic cards are interactive and send prompts to the assistant.
- Confirmed public contact channels are WhatsApp, LinkedIn and AhmedService.com.
