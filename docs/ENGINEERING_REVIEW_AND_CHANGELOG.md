# InterviewIQ — Engineering Notes, Changes, and Verification

**Repository:** [Sur2004/interview_iq](https://github.com/Sur2004/interview_iq)  
**Last reviewed:** 29 October 2026  
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

Markdown reports include answer revision entries with previous and updated text and timestamps. HTML export now renders Markdown headings, lists, code blocks, and tables into a printable HTML report, then sanitizes the generated markup to reduce script-injection risk. JSON export should still be checked against the current implementation before relying on it for a formal audit workflow.

### 3.4 Provider selection and key isolation

The sidebar's selected provider is now resolved into a single settings helper. Main interview scoring, answer revision scoring, and dynamic challenge generation receive the selected provider's key and model settings.

- Supported provider names are `groq`, `gemini`, `openai`, and `heuristic`.
- The helper selects the matching key name for the chosen provider.
- A provider-specific default model is used when the configured model belongs to a different provider; Gemini defaults to the currently documented `gemini-3.8-flash` model.
- Gemini requests send the API key in the `x-goog-api-key` header rather than placing it in the URL.
- Evaluator and dynamic-question paths both use the selected provider's model name instead of accidentally reusing a model configured for another provider.
- Evaluation and dynamic question generation route by the explicit provider, not by guessing the provider from the API-key prefix.
- If no key is available, the evaluation engine uses the offline heuristic path.

Keep API keys in environment variables or Streamlit Secrets. Do not commit real keys.

### 3.5 UI and usability improvements

- Replaced the seven fixed-width role tiles with a responsive grid that adapts to narrow screens.
- Added visible keyboard-focus styles and reduced-motion handling for users who disable animation.
- Replaced the misleading “LIVE” hero badge with a neutral “PRACTICE STUDIO” label.
- Made provider status contextual: offline mode is clearly identified, configured providers show the selected model, and missing provider keys produce a warning.
- Corrected the empty-state instruction to match the actual “Start Interview Round” button label.
- Improved the History page with a sortable category score table, compact session summary metrics, collapsed raw session JSON, and a confirmation step before deleting saved answers.
- Added Streamlit AppTest smoke tests for first render, offline-mode status, changing the target role, and starting a practice round.

### 3.6 Presentation-readiness and input robustness pass

- Refined the hero headline and first-run workspace copy to explain the product's core workflow, offline availability, and practice-only scoring in a clearer demo-friendly sequence.
- Added a parameterized offline-evaluator input matrix covering empty and short answers, irrelevant responses, relevant technical explanations, code snippets, STAR-style behavioral answers, filler-heavy and long answers, Unicode/symbols, prompt-injection wording, and a provided follow-up answer.
- Added UI journey tests that reject an empty answer without advancing the interview, and submit a valid technical answer, enter the follow-up stage, skip the follow-up, and verify the scored turn advances.
- Existing UI tests also cover role, experience level, interview type, and the maximum supported question count.
- The offline tests are deterministic and do not require a live provider key. They check score bounds, all four rubric dimensions, non-empty feedback, and presence of ethical disclaimers.
- Hosted evaluator instructions now explicitly treat candidate answers and background context as untrusted content, with a mocked-provider regression test for attempts to override the rubric or request an artificial score.
- Automated AppTest is not a substitute for visual inspection in a real browser; mobile screenshots, cross-browser layout, hosted-provider failure behavior, and the deployed Streamlit URL remain separate manual/browser verification tasks.

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

The suite includes checks for question banks, interview plan construction, rubric/evaluator behavior, SQLite CRUD/analytics, secret configuration, provider-key isolation, answer revision persistence, mocked Gemini model routing, sanitized HTML report rendering, and Streamlit UI smoke journeys plus a parameterized robustness matrix for varied answer inputs. See the current [Actions page](https://github.com/Sur2004/interview_iq/actions) for the latest test count and commit-specific result.

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
7. **Report formatting:** HTML export now uses Markdown rendering and sanitization, but should still be visually checked with long answers, unusual Markdown, and different browsers.
8. **UI test coverage:** The current CI suite is primarily unit/regression tests. It does not automate browser-based Streamlit interaction testing.

## 8. Suggested next improvements

Prioritized by reliability and user impact:

1. Extend mocked HTTP tests to cover Groq, OpenAI, Gemini dynamic-question generation, malformed provider responses, and offline fallback.
2. Add Streamlit AppTest or browser smoke tests for the main interview, revision editor, and technical challenge generator.
3. Preserve each prior evaluation alongside each answer revision for true before/after score comparison.
4. Add a dedicated JSON export regression test and check HTML/PDF output with long answers and unusual characters.
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
| Reports | Included answer revision history in Markdown and rendered/sanitized HTML output |
| Gemini integration | Updated default model and moved API key to request headers |
| Regression tests | Added mocked Gemini routing and HTML sanitization checks; latest reviewed run passed 19 tests |
| Code hygiene | Removed three obsolete app-rewrite scripts |
| CI | Added GitHub Actions pytest workflow and regression coverage |
| Documentation | Updated README and added this engineering/change guide |
| UI polish | Responsive role cards, accessible focus/reduced motion, clearer provider status, and safer history deletion |
| UI testing | Added Streamlit AppTest smoke tests for rendering and an offline interview flow |

## 10. Safety and privacy

- Never commit real API keys or credentials.
- Avoid entering confidential employer data, passwords, private customer data, or proprietary source code into interview responses.
- Use the feedback to improve your own authentic examples; do not present generated outlines as experiences you did not have.
- Treat all scores as practice indicators only.


## 10. Navigation and documentation follow-up (29 October 2026)

- Replaced the sidebar's radio-list navigation with a labeled **Open a section** dropdown to make workspace switching clearer on narrow screens and easier to operate.
- Added Streamlit AppTest smoke coverage for all non-default workspace destinations and a direct interaction test for opening **Resume & Project Review** from the selector.
- Updated the README and project report to explain the new navigation control and reflect the current guest-mode/browser-local-storage behavior instead of requiring SMTP/OTP sign-in.
- Updated the humanized project documentation to include all four team members and their responsibilities after the problem statement.
- Verification limitation: the repository was inspected through GitHub file access, but a full local test run and real-browser check of the deployed Streamlit app were not available during this review. The added automated tests must be confirmed by the GitHub Actions run, and the live app should be checked after deployment refresh.
