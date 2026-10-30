# Free-tier AI setup for InterviewIQ

InterviewIQ does not ship with shared API keys. Use your own provider keys, keep them in Streamlit Secrets or a local `.env`, and never commit secrets.

## Recommended: two-provider setup (voice + evaluation)

InterviewIQ uses separate services so audio transcription does not depend on the evaluation model:

- **Groq Whisper** transcribes recorded answers using `whisper-large-v3-turbo`.
- **Gemini Flash** evaluates typed and transcribed answers and generates feedback.
- In Auto provider mode, Gemini is preferred for evaluation when `GEMINI_API_KEY` is configured. Groq remains dedicated to transcription.

Create one key at [Groq Console](https://console.groq.com/keys) and one at [Google AI Studio](https://aistudio.google.com/apikey).

For local development, add to `.env`:
```dotenv
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here
LLM_PROVIDER=gemini
MODEL_NAME=gemini-3.8-flash
```

For Streamlit Community Cloud, open **App settings → Secrets** and add:
```toml
GROQ_API_KEY = "your_groq_key_here"
GEMINI_API_KEY = "your_gemini_key_here"
LLM_PROVIDER = "gemini"
MODEL_NAME = "gemini-3.8-flash"
```

Save/restart the app. In the provider settings, leave **Auto (via .env / Secrets)** selected to use Gemini for evaluation. Voice recording uses Groq Whisper automatically. You can test the selected evaluation provider with **Test AI API Connection**. The transcription key is checked when you submit an audio answer.

## Single-provider alternatives

- For Gemini-only evaluation, configure `GEMINI_API_KEY`. Voice transcription still requires `GROQ_API_KEY`.
- For Groq-only evaluation, configure `GROQ_API_KEY` and select Groq in provider settings. Voice transcription uses the same Groq key.

Provider free-tier availability, models, and quotas can change. Check your account dashboards for current limits.

Official references:
- [Gemini API pricing and free tier](https://ai.google.dev/gemini-api/docs/pricing)
- [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- [Groq rate limits](https://console.groq.com/docs/rate-limits)
- [Groq speech-to-text](https://console.groq.com/docs/speech-to-text)

## No key? Offline mode still works

Choose **Built-In Offline Engine** in the app. It provides local rubric diagnostics rather than hosted LLM feedback. Voice transcription still requires the Groq key; typed answers remain available without it.

## Privacy and review boundaries

- Recorded audio is sent to Groq for transcription. The resulting transcript is sent to the selected evaluation provider (Gemini in Auto mode when configured).
- A resume PDF is parsed locally into text. If a hosted LLM provider is configured and selected, that text and selected public repository snippets are sent to that provider for feedback.
- Repository review supports **public GitHub repositories only**. It reads a limited number of text files and never runs project code.
- Never paste API keys into the resume or repository URL field. Do not commit keys to Git.
- Provider terms and retention practices may apply to submitted prompts and audio. Do not upload confidential or highly sensitive material unless you have reviewed the providers' current terms.
- Feedback is for practice and project improvement, not a hiring decision. Confirm all findings manually.
