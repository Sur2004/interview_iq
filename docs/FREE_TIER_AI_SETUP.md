# Free-tier AI setup for InterviewIQ

InterviewIQ does not ship with a shared API key. Use your own provider key, keep it in Streamlit Secrets or a local `.env`, and never commit secrets.

## Recommended: Gemini API free tier

1. Open [Google AI Studio](https://aistudio.google.com/) and create an API key.
2. For local development, add this to `.env` (keep that file out of Git):
   ```dotenv
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=your_key_here
   MODEL_NAME=gemini-3.7-flash
   ```
3. For Streamlit Community Cloud, open **App settings → Secrets** and add:
   ```toml
   LLM_PROVIDER = "gemini"
   GEMINI_API_KEY = "your_key_here"
   MODEL_NAME = "gemini-3.7-flash"
   ```
4. Save/restart the app. The app uses the provider's current free-tier quotas where available. Free-tier availability, models, and limits can change; verify your own quota in AI Studio.

Official references:
- [Gemini API pricing and free tier](https://ai.google.dev/gemini-api/docs/pricing)
- [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)

## Alternative: Groq

Create a key in the [Groq Console](https://console.groq.com/), then set:
```dotenv
LLM_PROVIDER=groq
GROQ_API_KEY=your_key_here
MODEL_NAME=llama-3.3-70b-versatile
```
Check the [current Groq rate limits](https://console.groq.com/docs/rate-limits); availability and quotas depend on the account and model.

## No key? Offline mode still works

Choose **Built-In Offline Engine** in the app. Resume/project review then uses a basic checklist rather than an LLM. It does not execute code or provide semantic AI analysis.

## Privacy and review boundaries

- A resume PDF is parsed locally into text. If a hosted LLM provider is configured and selected, that text and selected public repository snippets are sent to that provider for feedback.
- Repository review supports **public GitHub repositories only**. It reads a limited number of text files and never runs project code.
- Never paste API keys into the resume or repository URL field. Do not commit keys to Git.
- Free-tier provider terms can allow submitted prompts/content to be used to improve provider products. Do not upload confidential or highly sensitive material unless you have reviewed the provider's current terms and are comfortable with them.
- Feedback is for practice and project improvement, not a hiring decision. Confirm all findings manually.
