# InterviewIQ Project Report

## 1. Introduction
InterviewIQ is a web-based application that helps students practise interview questions and improve their answers. Users select an interview role or practice mode, respond to questions, and receive AI-generated scores, explanations, and suggestions. The application combines a Streamlit interface with Python backend logic and configurable Large Language Model (LLM) providers.

## 2. Problem Statement
Students may practise interviews without clear feedback on whether answers are relevant, well-structured, specific, and complete. Personal coaching is not always available, and self-assessment can be inconsistent. InterviewIQ brings question practice, answer evaluation, and performance review together in one application.

## 3. Objectives
- Provide a simple platform for role-based interview practice.
- Use an LLM provider to evaluate answers and generate feedback.
- Help users identify strengths and areas for improvement.
- Support voice-recorded answers in supported provider configurations.
- Present practice results and downloadable reports clearly.

## 4. Technologies Used
- **Python:** Application logic, backend processing, evaluation flow, and report preparation.
- **Streamlit:** Web interface, navigation, audio input, results, and downloads.
- **LLM APIs:** Answer evaluation, feedback generation, and supported speech transcription.
- **Python libraries:** API communication, data handling, PDF text extraction, and application utilities.
- **Browser localStorage:** Profile and practice-history data for the current browser; history does not automatically sync across devices.

## 5. System Workflow — How It Works
1. The user opens InterviewIQ and chooses a workspace from the sidebar **Open a section** dropdown, then selects an interview role or practice mode.
2. The application presents a question appropriate to the selected mode.
3. The user records a spoken answer in voice-enabled interview rounds.
4. A supported configured provider transcribes the audio; the Python backend evaluates the question and answer.
5. The evaluator returns a score, explanation, and suggestions.
6. Where supported, a follow-up question is presented and the next response is evaluated.
7. The user reviews performance and exports available session summaries or reports.

## 6. Main Features
- Role-based interview practice and question display.
- AI-assisted answer evaluation with scores and improvement suggestions.
- Follow-up questions in supported interview modes.
- Voice-answer workflow using browser audio recording and configured-provider transcription.
- Camera preview and browser visibility-change counter as basic interview-monitoring aids.
- Practice analytics and local history where configured.
- Exportable practice reports and JSON session data.
- Optional resume and public GitHub project review.
- Sidebar workspace navigation through the **Open a section** dropdown.

## 7. Team Members, Roles, and Assigned Work

### K. V. N. Surya Teja — Backend and API Developer
Develop the Python backend; integrate the LLM API; handle question flow and follow-up logic; connect transcription and evaluation; and return scores and feedback to the interface.

### G. Tejesh — Frontend Developer
Build the application screens and navigation; connect interface controls to backend functions; and ensure questions, answer capture, scores, and feedback are displayed clearly.

### A. Bhagyaraju — UI/UX Designer
Design a clear and consistent experience for role selection, interview questions, answer recording, evaluation results, and feedback. Review layout and usability.

### G. Jhon — Documentation
Prepare the project report and presentation; document technologies, workflow, features, test cases, limitations, and future enhancements.

## 8. Navigation, Testing, and Limitations
The repository includes automated tests for key application behaviour, including smoke tests that open each main workspace and check that it renders without Streamlit exceptions. Automated tests do not confirm that every browser permission, microphone, camera, or hosted deployment path works on every device. Results can vary with the configured provider, API availability, audio quality, and submitted answer. AI feedback is practice guidance, not a guarantee of interview success.

The camera component requests browser permission and displays a preview; it is not designed to record or save video. The tab-switch counter detects certain browser visibility changes, but cannot prevent switching tabs or reliably identify external assistance, another device, or all forms of misconduct. These are basic monitoring aids, not a complete proctoring system, and need manual testing in the deployed browser.

Voice recordings are sent to the selected supported provider for transcription. Users should configure their own API credentials and avoid recording sensitive personal information.

## 9. Conclusion and Future Scope
InterviewIQ combines a web interface with LLM-assisted evaluation to help students practise interviews and review their performance. Its voice workflow and basic interview-monitoring indicators extend practice beyond typed answers. Future improvements could include broader role-specific question banks, progress tracking across sessions, stronger automated UI testing, improved transcription error handling, and more detailed analytics. Any additional monitoring should be transparent, consent-based, and privacy-conscious.

## Project Links
- GitHub: https://github.com/Sur2004/interview_iq
- Deployed app: https://interviewiq-jinjpnyj6pmcyodyyjusnj.streamlit.app/
