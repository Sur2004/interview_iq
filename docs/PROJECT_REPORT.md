# InterviewIQ — Project Report

## 1. Introduction
InterviewIQ is a web-based application that helps students practise interview questions and improve their answers. Users select an interview role or practice mode, answer questions, and receive AI-generated scores, explanations, and suggestions. It combines a Streamlit interface with Python backend logic and configurable Large Language Model (LLM) providers.

## 2. Problem Statement
Students may practise interviews without knowing whether their answers are relevant, clear, well-structured, or complete. Personal feedback can be difficult to obtain when a mentor is unavailable. InterviewIQ brings practice questions, automated evaluation, and performance review together in one application.

## 3. Objectives
- Provide a simple platform for role-based interview practice.
- Use an LLM provider to assess answers and generate actionable feedback.
- Help users identify strengths and areas for improvement.
- Support voice-recorded answers in supported provider configurations.
- Present practice results and downloadable reports clearly.

## 4. Technologies Used
- **Python:** application logic, backend processing, evaluation flow, and report preparation.
- **Streamlit:** web interface, navigation, answer capture, results, and downloads.
- **LLM APIs:** answer evaluation and supported speech transcription.
- **Python libraries:** API communication, data handling, PDF text extraction, and application utilities.
- **SQLite/local storage:** practice history and analytics where configured.

## 5. System Workflow
1. The user opens InterviewIQ and selects a role or practice section.
2. The application presents a question for the selected mode.
3. In voice-enabled rounds, the user records a spoken answer and the selected supported provider transcribes it.
4. The backend sends the question and answer to the configured evaluator, or uses the available fallback evaluation path.
5. The evaluator returns a score, explanation, and improvement suggestions.
6. A follow-up question may be presented in supported modes.
7. The user reviews performance and exports available reports.

## 6. Main Features
- Role-based interview practice.
- AI-assisted answer evaluation with scores and suggestions.
- Follow-up questions in supported modes.
- Voice-answer workflow using browser audio recording and provider transcription.
- Camera preview and browser visibility-change counter as basic monitoring aids.
- Practice analytics and local history where configured.
- Exportable reports and JSON session data.
- Optional resume and public GitHub project review.

## 7. Team Members, Roles, and Assigned Work

### K. V. N. Surya Teja — Backend and API Developer
Develop the Python backend; integrate the LLM API; handle question flow and follow-ups; connect transcription and evaluation; and return scores and feedback to the interface.

### G. Tejesh — Frontend Developer
Build application screens and navigation; connect interface controls to backend functions; and ensure questions, answer capture, scores, and feedback are displayed clearly.

### A. Bhagyaraju — UI/UX Designer
Design a clear and consistent experience for role selection, questions, answer recording, evaluation results, and feedback. Review layout and usability.

### G. Jhon — Documentation
Prepare the project report and presentation; document technologies, workflow, features, test cases, limitations, and future enhancements; and maintain final documentation.

## 8. Testing and Limitations
The repository includes automated tests for key application and evaluation behaviour. Automated tests do not guarantee every browser permission, microphone, camera, or hosted deployment path works on every device. Results can vary with provider availability, audio quality, and answer content. The camera component requests permission and displays a preview; it is not designed to record or save video. The tab-switch counter detects certain browser visibility changes but cannot prevent switching tabs or reliably identify external assistance. These are basic monitoring aids, not a complete proctoring system, and require manual testing in the deployed app. Voice recordings are sent to the selected supported provider for transcription.

## 9. Conclusion and Future Scope
InterviewIQ combines a web interface with LLM-assisted evaluation to help students practise interviews and review performance. Future improvements could include broader role-specific question banks, cross-session progress tracking, stronger automated UI tests, improved transcription error handling, and more detailed analytics. Monitoring should remain transparent, consent-based, and privacy-conscious.

## Project Links
- GitHub: https://github.com/Sur2004/interview_iq
- Deployed app: https://interviewiq-jinjpnyj6pmcyodyyjusnj.streamlit.app/
