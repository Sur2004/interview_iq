# InterviewIQ — Engineering Notes, Changes, and Verification

**Repository:** [Sur2004/interview_iq](https://github.com/Sur2004/interview_iq)  
**Last reviewed:** 24 October 2026  
**Purpose:** Record the application architecture, answer-revision feature, reliability/security changes, review findings, verification steps, and known limitations.

## 1. Product overview

InterviewIQ is a Streamlit application for technical and behavioral interview practice. It combines curated questions, optional hosted-LLM feedback, an offline heuristic evaluator, session history, analytics, and practice report exports. Feedback is formative and must not be interpreted as a hiring prediction.

### Main areas

- **Mock Interview Studio:** A multi-turn interview flow with a primary answer, contextual follow-up, rubric scoring, and a session report.
- **AI Technical Challenge Generator:** Creates a custom technical question from a topic and difficulty, accepts an answer, and returns rubric feedback.
- **Spot the Flaw Game:** Practice identifying weak interview responses.
- **STAR Story Builder:** Helps structure authentic project/coursework examples.
- **Question Bank / Playbooks / Analytics / Reports / Rubric:** Supporting question discovery, learning guidance, progress review, report export, and rubric explanation.
- **History page:** Lists stored sessions, aggregate practice statistics, and session detail data.

## 2. Architecture and source-of-truth files

| File | Responsibility |
| --- | --- |
| `app.py` | Streamlit UI, session state, interview workflow, provider selection, challenge generator, and answer revision editor |
| `backend/models.py` | Dataclasses and enums for questions, turns, sessions, rubric scores, and evaluations |
| `backend/question_bank.py` | Curated question bank and interview-plan construction |
| `backend/evaluator.py` | Provider-backed evaluation, offline heuristic evaluation, follow-up generation, technical analysis, and dynamic question generation |
| `backend/config.py` | Reads provider settings and secrets from Streamlit Secrets, environment variables, and optional `.env` |
| `backend/database.py` | SQLite schema, session persistence, CRUD, and aggregate analytics |
| `backend/report_generator.py` | Markdown and printable HTML report generation |
| `pages/1_History.py` | Session history and aggregate performance view |
| `tests/test_interview_iq.py` | Unit and regression tests |
| `.github/workflows/tests.yml` | Runs pytest on pushes, pull requests, and manual workflow dispatch |
| `.streamlit/config.toml` | Streamlit server configuration, including CORS/XSRF protections |
| `README.md` | User-facing project description, setup, configuration, usage, and limitations |

Three obsolete rewrite scripts (`clean_app.py`, `fix_tab_studio.py`, and `rebuild_sidebar.py`) were removed because they performed direct, brittle source rewrites of `app.py`. They are not runtime dependencies.

## 3. Changes made in this review

### 3.1 Editable responses in the Mock Interview Studio

Completed answers can now be revised from:
- the current turn's result panel;
- the completed session's turn-by-turn transcript; and
- the “Review or edit previous answers” area while progressing through later questions.

The editor supports both the main answer and the follow-up answer. It prevents an empty main answer from being saved and tells the user when no changes have been made.

### 3.2 Re-scoring and persistence

When a revision is saved:
1. The old and new answer text are added to `InterviewTurn.answer_revisions` with the field name and timestamp.
2. The current main/follow-up answer values are updated.
3. The evaluator is run again against the revised text.
4. The turn is marked completed and its timestamp is updated.
5. The session's aggregate score is recomputed from turns that have an evaluation.
6. `save_session()` writes the updated session JSON and turn rows to SQLite.

Revision history is serialized by `InterviewTurn.to_dict()`, so the existing session JSON field stores it without a separate schema migration. Existing saved session JSON from before this feature may not contain `answer_revisions`; the editor uses the model's default empty list for newly created turns. Legacy stored JSON is displayed as raw session data on the History page and is not automatically migrated into a live `InterviewSession` object.

### 3.3 Reports

Markdown reports now identify the response as the latest response and include revision entries with the previous and updated text and timestamp. HTML report export wraps the Markdown report in a printable page. JSON export should be checked against the current implementation before relying on it for a formal audit workflow.

### 3.4 Provider selection and key isolation

The sidebar's selected provider is now resolved into a single settings helper. Main interview scoring, answer revision scoring, and dynamic challenge generation receive the selected provider's key and model settings.

- Supported provider names are `groq`, `gemini`, `openai`, and `heuristic`.
- The helper selects the matching key name for the chosen provider.
- A provider-specific default model is used when the configured model belongs to a different provider.
- Evaluation and dynamic question generation route by the explicit provider, not by guessing the provider from the API-key prefix.
- If no key is available, the evaluation engine uses the offline heuristic path.

Keep API keys in environment variables or Streamlit Secrets. Do not commit real keys.

### 3.5 Security and reliability changes made earlier

- Enabled Streamlit CORS and XSRF protection in `.streamlit/config.toml`.
- Corrected analytics so all sessions are counted, including sessions that do not yet have scores. The average session score is computed separately from the joined turn table.
- Added missing `Any` imports used by type annotations.
- Replaced the removed `st.experimental_rerun()` call with `st.rerun()` in the History page.
- Corrected repository/demo links and connected the README test badge to GitHub Actions.
- Added a pytest workflow that runs the test suite for changes to `main` and pull requests.

## 4. User workflow

### Mock interview

1. Set the candidate name, target role, experience level, interview type, interviewer persona, number of questions, and optional project/coursework context in the sidebar.
2. Select the AI provider in the provider panel and configure the matching API key if using a hosted model. The offline engine is available without a key.
3. Click **Start Interview Round**.
4. Submit the main answer; respond to the follow-up question; review the score and rubric feedback.
5. Use **Edit answer and refresh feedback** to revise either answer and re-score.
6. While on a later question, use **Review or edit previous answers** to revisit a completed turn.
7. Finish the round and export a report from the report tab.

### Custom technical challenge

1. Open the technical challenge generator.
2. Enter a focused topic and choose the desired difficulty.
3. Generate the question and read the follow-up and rubric hints.
4. Write an answer in the answer box.
5. Select **Score / update feedback**.
6. Revise the text and submit again to evaluate the updated response.

## 5. Rubric and evaluation behavior

The visible rubric has four criteria, each scored from 1 to 5:

- **Relevance & Directness:** Does the answer address the question?
- **Structure & Framework:** Is the response logically organized?
- **Evidence & Ownership:** Does it include specific reasoning and authentic personal contribution?
- **Clarity & Communication:** Is it understandable and appropriately concise?

The hosted model may fail because of network errors, provider limits, invalid configuration, or response-format issues. The evaluator is designed to fall back to heuristic evaluation in error/no-key cases. Heuristic scores are approximate practice feedback, not equivalent to human expert assessment.

## 6. Tests and verification

Run locally from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m pytest -q tests
streamlit run app.py
```

On Windows, activate the environment with `.venv\\Scripts\\activate.bat` or `.venv\\Scripts\\Activate.ps1`.

The suite includes checks for question banks, interview plan construction, rubric/evaluator behavior, SQLite CRUD/analytics, secret configuration, provider-key isolation, and answer revision persistence. GitHub Actions runs the same test command. The latest successful run should be checked on the [Actions page](https://github.com/Sur2004/interview_iq/actions) rather than assuming a newly pushed commit has passed.

### Manual smoke-test checklist

- [ ] App starts without import or Streamlit configuration errors.
- [ ] Offline mode can start a mock interview without an API key.
- [ ] A full interview can submit a main answer, follow-up answer, and complete a turn.
- [ ] The current turn's main answer can be revised and re-scored.
- [ ] The follow-up answer can be revised and re-scored.
- [ ] An earlier completed turn can be edited while on a later turn.
- [ ] Revision history shows previous and updated text with timestamps.
- [ ] Reloading session details preserves the revision entries.
- [ ] The final Markdown/HTML report includes revision history.
- [ ] The dynamic challenge generator can generate, score, edit, and re-score.
- [ ] Each configured provider routes only to its own endpoint and falls back gracefully on error.
- [ ] History analytics, report downloads, and deletion behave as expected.
- [ ] The deployed Streamlit app reflects the latest GitHub commit.

## 7. Review findings and remaining risks

These items should be treated as follow-up work, not as verified fixes:

1. **Provider credentials and manual override:** The UI's manual API-key override is intended for the selected provider. A key for the wrong provider may fail; provider key formats should not be used as a substitute for choosing the correct provider. Never paste keys into issue reports or commit history.
2. **Persistent cloud storage:** A local SQLite file on ephemeral hosting may be reset when the service sleeps or redeploys. Use a persistent managed database if durable cloud history is a requirement.
3. **Revision audit semantics:** Revision history currently stores the answer text, field name, and timestamp, but not a full immutable copy of each prior evaluation result. The current score is updated after re-scoring.
4. **Concurrent writes:** SQLite is suitable for small single-instance practice use; simultaneous multi-user production traffic may need a managed database and explicit concurrency testing.
5. **External dependencies:** Mermaid rendering depends on a browser-accessible CDN. Network restrictions can prevent diagrams from rendering while the rest of the page works.
6. **Live deployment:** A successful GitHub Actions run validates the automated tests but does not prove that Streamlit Community Cloud has completed deployment or that every UI interaction works in a browser. Perform the manual smoke test after deployment.
7. **Report formatting:** The HTML export is a printable wrapper around Markdown text, not a full Markdown-to-HTML renderer. It is readable and printable, but Markdown syntax may remain visible. A proper Markdown renderer can be added if polished HTML/PDF output is required.
8. **UI test coverage:** The current CI suite is primarily unit/regression tests. It does not automate browser-based Streamlit interaction testing.

## 8. Suggested next improvements

Prioritized by reliability and user impact:

1. Add automated tests for provider endpoint selection and offline fallback using mocked HTTP requests.
2. Add Streamlit AppTest or browser smoke tests for the main interview, revision editor, and technical challenge generator.
3. Preserve each prior evaluation alongside each answer revision for true before/after score comparison.
4. Render reports with a Markdown library and add a dedicated JSON export regression test.
5. Add safe session recovery/loading if users need to resume saved sessions after a browser refresh.
6. Consider a persistent database for deployed multi-user use and add database backup/export controls.

## 9. Change history summary

| Area | Change |
| --- | --- |
| Streamlit security | Enabled CORS/XSRF protections |
| Evaluator | Fixed provider-key selection and explicit endpoint routing |
| Analytics | Corrected session counts and score aggregation |
| Compatibility | Fixed missing typing imports and updated rerun API |
| Technical challenge | Added an editable answer box and re-scoring flow |
| Mock interview | Added editing for current, previous, and completed answers |
| Persistence | Added timestamped answer revision records to session JSON |
| Reports | Included answer revision history in Markdown output |
| Code hygiene | Removed three obsolete app-rewrite scripts |
| CI | Added GitHub Actions pytest workflow and regression coverage |
| Documentation | Updated README and added this engineering/change guide |

## 10. Safety and privacy

- Never commit real API keys or credentials.
- Avoid entering confidential employer data, passwords, private customer data, or proprietary source code into interview responses.
- Use the feedback to improve your own authentic examples; do not present generated outlines as experiences you did not have.
- Treat all scores as practice indicators only.
