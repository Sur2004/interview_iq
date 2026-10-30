"""
Curated Question Bank & STAR Methodology Prompts for InterviewIQ.
Covers Behavioral, Role-Specific Technical, and Project-Explanation domains.
"""

from typing import List, Dict, Optional
import random
import uuid
from .models import QuestionCategory, QuestionItem, TargetRole, InterviewType


BEHAVIORAL_QUESTIONS: List[Dict] = [
    {
        "id": "beh_01",
        "competency": "Teamwork & Collaboration",
        "question_text": "Tell me about a time you worked on a team project where members had conflicting opinions on the direction. How did you handle it?",
        "rubric_hints": [
            "Clear Situation setting the project context and deadline",
            "Specific Task detailing your role in the disagreement",
            "Action describing objective evaluation, compromise, and communication",
            "Result highlighting the delivered project and team morale impact"
        ],
        "default_followup": "If a team member had remained unconvinced despite the group consensus, how would you have kept the project moving forward without alienating them?",
    },
    {
        "id": "beh_02",
        "competency": "Overcoming Failure & Resilience",
        "question_text": "Describe a project or assignment where things went significantly wrong or didn't meet expectations. What happened and what did you learn?",
        "rubric_hints": [
            "Honest ownership without blaming teammates or external circumstances",
            "Root-cause analysis of what went wrong",
            "Immediate remediation steps taken",
            "Long-term takeaways applied to subsequent work"
        ],
        "default_followup": "Looking back, what early warning signal did you overlook, and what check would you introduce today to catch it sooner?",
    },
    {
        "id": "beh_03",
        "competency": "Initiative & Leadership",
        "question_text": "Give an example of a situation where you identified a problem that no one asked you to solve and took the initiative to fix it.",
        "rubric_hints": [
            "Clear identification of the inefficiency, bug, or gap",
            "Proactive research and proof-of-concept",
            "Stakeholder or peer buy-in without overstepping boundaries",
            "Measurable time saved, bug reduction, or improved workflow"
        ],
        "default_followup": "How did you prioritize this unsolicited initiative against your primary assigned deliverables?",
    },
    {
        "id": "beh_04",
        "competency": "Prioritization & Tight Deadlines",
        "question_text": "Tell me about a time when you were overwhelmed with multiple competing deadlines. How did you prioritize and execute?",
        "rubric_hints": [
            "Systematic prioritization framework (impact vs urgency)",
            "Proactive communication with professors, managers, or stakeholders",
            "Disciplined execution and trade-off management",
            "Successful delivery of high-impact goals"
        ],
        "default_followup": "What specific task did you choose to de-prioritize or drop, and how did you communicate that trade-off?",
    },
    {
        "id": "beh_05",
        "competency": "Handling Ambiguity",
        "question_text": "Walk me through a situation where you had to work with vague or constantly shifting requirements. How did you determine what to build?",
        "rubric_hints": [
            "Deconstructing ambiguous problem statements into testable hypotheses",
            "Asking clarifying questions and creating lightweight prototypes",
            "Iterative validation with users or mentors",
            "Final delivered outcome matching actual user need"
        ],
        "default_followup": "What assumption did you make early on that turned out to be wrong, and how quickly did you pivot?",
    },
    {
        "id": "beh_06",
        "competency": "Receiving Critical Feedback",
        "question_text": "Describe an occasion where you received harsh or unexpected critical feedback on your work. How did you respond?",
        "rubric_hints": [
            "Receptive, non-defensive mindset",
            "Clarifying questions to understand the underlying gap",
            "Concrete revisions made based on feedback",
            "Observable improvement in subsequent iterations"
        ],
        "default_followup": "How do you distinguish between constructive technical feedback and subjective stylistic preference when revising your work?",
    },
    {
        "id": "beh_07",
        "competency": "Stakeholder & Client Communication",
        "question_text": "Tell me about a time you had to explain a complex technical concept or constraint to a non-technical stakeholder or teammate.",
        "rubric_hints": [
            "Eliminating jargon and using intuitive analogies",
            "Focusing on user/business impact rather than implementation weeds",
            "Checking for comprehension actively",
            "Gaining alignment on the proposed solution"
        ],
        "default_followup": "How did you confirm that the stakeholder genuinely understood the trade-off rather than just nodding along?",
    },
]

PROJECT_QUESTIONS: List[Dict] = [
    {
        "id": "proj_01",
        "competency": "Architecture & System Design",
        "question_text": "Walk me through the architecture of a significant technical project you built. What were the key components, and why did you choose that stack?",
        "rubric_hints": [
            "High-level system topology (frontend, backend, persistence, external services)",
            "Clear technical justification for stack choices over alternatives",
            "Data flow from user interaction to storage",
            "Explicit mention of your personal contributions vs library defaults"
        ],
        "default_followup": "If user traffic or dataset size increased by a factor of 100x tomorrow, which specific bottleneck would fail first and how would you redesign it?",
    },
    {
        "id": "proj_02",
        "competency": "Debugging & Troubleshooting",
        "question_text": "Tell me about the most difficult bug, performance regression, or system issue you encountered in your project. How did you isolate and resolve it?",
        "rubric_hints": [
            "Specific symptoms and reproduction steps",
            "Hypothesis-driven debugging methodology (logs, profiler, binary search)",
            "Root-cause discovery rather than just treating symptoms",
            "Preventive regression test or monitoring introduced"
        ],
        "default_followup": "What tooling or telemetry would have cut your troubleshooting time in half for that bug?",
    },
    {
        "id": "proj_03",
        "competency": "Technical Trade-Offs",
        "question_text": "Describe an engineering trade-off you had to make in one of your projects (e.g., speed vs accuracy, consistency vs availability, simplicity vs extensibility). What was the decision?",
        "rubric_hints": [
            "Clear definition of both alternatives and their respective costs",
            "Contextual rationale for the chosen path",
            "Downstream consequences and mitigation strategies",
            "Evaluation of whether the decision held up over time"
        ],
        "default_followup": "Under what new constraints or requirements would the alternate choice have been the superior decision?",
    },
    {
        "id": "proj_04",
        "competency": "Technical Retrospective",
        "question_text": "If you were to rewrite your flagship project from scratch today with the knowledge you now possess, what would you architect differently?",
        "rubric_hints": [
            "Honest critical evaluation of initial naive assumptions",
            "Specific modern architectural or library patterns proposed",
            "Code quality, testing, or modularity improvements",
            "Clear demonstration of technical growth"
        ],
        "default_followup": "What is the single biggest lesson from that project that you now apply by default to every new project?",
    },
]

TECHNICAL_QUESTIONS_BY_ROLE: Dict[str, List[Dict]] = {
    TargetRole.SOFTWARE_ENGINEERING.value: [
        {
            "id": "swe_tech_01",
            "topic": "API Design & Protocol Choices",
            "question_text": "Compare RESTful APIs with GraphQL or gRPC. In what scenario would you choose REST over GraphQL, and vice versa?",
            "rubric_hints": [
                "Over-fetching and under-fetching nuances",
                "HTTP caching semantics, schema typing, and tooling",
                "Network overhead and client flexibility",
                "Practical production trade-offs for web or mobile apps"
            ],
            "default_followup": "How do you handle rate-limiting and query complexity attacks in a GraphQL endpoint compared to traditional REST?",
        },
        {
            "id": "swe_tech_02",
            "topic": "Database Indexing & Performance",
            "question_text": "Explain how database indexes (such as B-Tree indexes) speed up query lookups. What are the write and storage trade-offs of adding multiple indexes?",
            "rubric_hints": [
                "B-Tree logarithmic search mechanics vs full table scans",
                "Write amplification during INSERT, UPDATE, and DELETE operations",
                "Composite index column ordering (leading prefix rule)",
                "Index selectivity and query planner considerations"
            ],
            "default_followup": "Suppose an `EXPLAIN ANALYZE` reveals a sequential scan despite an index existing on that column. What reasons could cause the query planner to bypass the index?",
        },
        {
            "id": "swe_tech_03",
            "topic": "Concurrency & Race Conditions",
            "question_text": "What is a race condition in a multi-threaded or distributed environment? How do you prevent race conditions when updating shared state?",
            "rubric_hints": [
                "Check-then-act and read-modify-write hazards",
                "Pessimistic locking vs Optimistic concurrency control (OCC with versioning)",
                "Atomic operations and database transaction isolation levels",
                "Deadlock hazards and avoidance strategies"
            ],
            "default_followup": "When would you prefer optimistic locking over pessimistic database row locks in a high-traffic web application?",
        },
        {
            "id": "swe_tech_04",
            "topic": "Caching Strategies & Invalidation",
            "question_text": "Explain the Cache-Aside (Lazy Loading) pattern. What problems arise when cached data falls out of sync with the primary database, and how do you mitigate them?",
            "rubric_hints": [
                "Read flow: cache hit vs cache miss and DB fetch",
                "Write flow: updating DB and evicting or updating cache",
                "Cache stampede (thundering herd) and TTL strategies",
                "Eventual consistency and race conditions on concurrent writes"
            ],
            "default_followup": "How would you prevent a cache stampede when a frequently accessed cache key expires during peak traffic?",
        },
    ],
    TargetRole.FRONTEND_ENGINEERING.value: [
        {
            "id": "fe_tech_01",
            "topic": "Web Performance Optimization",
            "question_text": "How do you diagnose and optimize web page load performance? Walk through metrics like Largest Contentful Paint (LCP) and Cumulative Layout Shift (CLS).",
            "rubric_hints": [
                "Core Web Vitals definitions (LCP, CLS, INP/FID)",
                "Asset optimization (compression, next-gen formats, responsive images)",
                "Code splitting, bundle analysis, and tree shaking",
                "Critical rendering path, preload/prefetch tags"
            ],
            "default_followup": "If a heavy third-party analytics script is delaying your LCP and blocking the main thread, how would you remediate it?",
        },
        {
            "id": "fe_tech_02",
            "topic": "State Management & Reactivity",
            "question_text": "Compare local component state, context/provider state, and external store management (like Redux or Zustand). How do you decide where a piece of state should live?",
            "rubric_hints": [
                "Prop drilling avoidance vs unnecessary re-rendering blast radius",
                "Colocation principle: keeping state as close to consumption as possible",
                "Server state (caching/invalidation) vs Client UI state",
                "Performance profiling for memoization (`useMemo`, `useCallback`)"
            ],
            "default_followup": "Why can excessive use of React Context cause performance bottlenecks in high-frequency update scenarios?",
        },
        {
            "id": "fe_tech_03",
            "topic": "Frontend Security",
            "question_text": "What is Cross-Site Scripting (XSS) and Cross-Site Request Forgery (CSRF)? How do modern frontend frameworks and HTTP headers defend against them?",
            "rubric_hints": [
                "DOM-based, Reflected, and Stored XSS mechanics",
                "Content Security Policy (CSP) and framework auto-escaping",
                "SameSite cookie attributes and CSRF anti-forgery tokens",
                "Safe handling of third-party user inputs and markdown rendering"
            ],
            "default_followup": "If you must render rich HTML user input (e.g., in a comment system), what exact precautions do you implement?",
        },
    ],
    TargetRole.DATA_SCIENCE_ML.value: [
        {
            "id": "ds_tech_01",
            "topic": "Bias-Variance Trade-off & Regularization",
            "question_text": "Explain the Bias-Variance trade-off. What diagnostic techniques tell you whether your model suffers from high bias or high variance, and how do you resolve each?",
            "rubric_hints": [
                "High bias = underfitting (oversimplified model, poor train and validation scores)",
                "High variance = overfitting (memorizing noise, low train error, high validation gap)",
                "Learning curves and cross-validation analysis",
                "Remedies: L1/L2 regularization, dropout, pruning, feature engineering, more data"
            ],
            "default_followup": "How do L1 (Lasso) and L2 (Ridge) regularization mathematically differ in how they treat feature weights?",
        },
        {
            "id": "ds_tech_02",
            "topic": "Evaluation Metrics for Imbalanced Datasets",
            "question_text": "Why is accuracy a misleading metric for imbalanced classification tasks (e.g., fraud detection at 99.5% negative rate)? What metrics would you use instead and why?",
            "rubric_hints": [
                "Accuracy paradox on majority class dominance",
                "Precision, Recall, F1-Score, and PR-AUC vs ROC-AUC",
                "Cost-benefit trade-off of False Positives vs False Negatives in business context",
                "Resampling methods (SMOTE, under-sampling) and class weights"
            ],
            "default_followup": "If your fraud detection model has 98% precision but only 20% recall, what is the business consequence, and how would you adjust the decision threshold?",
        },
        {
            "id": "ds_tech_03",
            "topic": "Data Leakage & Cross-Validation",
            "question_text": "What is data leakage in machine learning, and what are common subtle ways it enters a modeling pipeline during data preprocessing?",
            "rubric_hints": [
                "Fitting scalers, imputers, or encoders on the whole dataset prior to splitting",
                "Temporal leakage in time-series forecasting",
                "Target leakage (features containing downstream proxy signals)",
                "Strict pipeline encapsulation (`sklearn.pipeline.Pipeline`)"
            ],
            "default_followup": "How would you structure cross-validation for customer churn prediction where each user has multiple historical transaction rows?",
        },
    ],
    TargetRole.PRODUCT_MANAGEMENT.value: [
        {
            "id": "pm_tech_01",
            "topic": "Product Prioritization Frameworks",
            "question_text": "Walk me through how you prioritize feature requests when engineering capacity is constrained. Which prioritization frameworks have you used or evaluated?",
            "rubric_hints": [
                "Frameworks like RICE (Reach, Impact, Confidence, Effort) or Value vs Effort matrix",
                "Aligning feature bets with top-line company OKRs",
                "Balancing quick wins, technical debt, and high-impact strategic bets",
                "Managing stakeholder expectations with data-backed transparency"
            ],
            "default_followup": "How do you defend your prioritization score when a vocal executive demands their pet feature be pushed ahead?",
        },
        {
            "id": "pm_tech_02",
            "topic": "Metrics & Metric Diagnosis",
            "question_text": "Suppose a major core metric (e.g., 7-day retention or checkout conversion) dropped by 12% week-over-week. How would you systematically investigate the root cause?",
            "rubric_hints": [
                "Data verification (logging bugs, pipeline latency, instrumentation changes)",
                "Segmenting by dimension (platform, browser, geography, new vs returning)",
                "Correlating with recent deployments, feature flags, or marketing campaigns",
                "External factors (holidays, competitor launches, seasonality)"
            ],
            "default_followup": "If the drop is isolated specifically to Android users in one country, what are your immediate next three diagnostic steps?",
        },
    ],
    TargetRole.DEVOPS_CLOUD.value: [
        {
            "id": "devops_tech_01",
            "topic": "CI/CD & Deployment Strategies",
            "question_text": "Compare Blue-Green deployments with Canary releases. What are the operational trade-offs and database migration complexities for each?",
            "rubric_hints": [
                "Blue-Green: instant traffic switch, fast rollback, requires double idle infrastructure",
                "Canary: progressive routing (1% -> 5% -> 25% -> 100%), real user telemetry validation",
                "Database backward/forward schema compatibility (Expand & Contract pattern)",
                "Automated health checks and automated rollback triggers"
            ],
            "default_followup": "How do you handle zero-downtime database schema migrations when a table column is renamed in a Canary rollout?",
        },
        {
            "id": "devops_tech_02",
            "topic": "Infrastructure as Code & Drift",
            "question_text": "Explain how Infrastructure as Code (IaC) tools like Terraform manage state. What is configuration drift and how do you detect and remediate it?",
            "rubric_hints": [
                "Terraform state file as source of truth mapping config to cloud resources",
                "Remote backend state storage with distributed locking (S3 + DynamoDB)",
                "Drift detection via `terraform plan` and scheduled drift reconcilers",
                "Strict CI/CD policy preventing manual out-of-band console changes"
            ],
            "default_followup": "What happens if two engineers execute `terraform apply` concurrently without remote state locking?",
        },
    ],
    TargetRole.AI_LLM_ENGINEERING.value: [
        {
            "id": "ai_tech_01",
            "topic": "Retrieval-Augmented Generation (RAG) Architecture",
            "question_text": "Explain the architecture of a Retrieval-Augmented Generation (RAG) system. What chunking strategies and embedding distance metrics do you evaluate?",
            "rubric_hints": [
                "Document chunking strategies (fixed-size vs recursive character vs semantic boundary)",
                "Embedding vector search mechanics (Cosine Similarity vs Dot Product vs Euclidean)",
                "Vector database indexing (HNSW vs IVFFlat)",
                "Reranking models and context window budget management"
            ],
            "default_followup": "How do you detect and prevent hallucinations when the vector database retrieves irrelevant or contradictory context chunks?",
        },
        {
            "id": "ai_tech_02",
            "topic": "Fine-Tuning vs RAG vs Prompt Engineering",
            "question_text": "How do you decide between Prompt Engineering, RAG, and Parameter-Efficient Fine-Tuning (PEFT/LoRA) for an enterprise domain problem?",
            "rubric_hints": [
                "Trade-offs in cost, latency, update frequency, and hallucination risk",
                "RAG for dynamic factual knowledge retrieval",
                "LoRA/PEFT for teaching specialized tone, vocabulary, or strict output syntax",
                "Evaluation frameworks (RAGAS, BLEU, ROUGE, human evaluation)"
            ],
            "default_followup": "Suppose your fine-tuned model begins suffering from catastrophic forgetting on general queries. What mitigation steps do you take?",
        },
    ],
    TargetRole.CYBERSECURITY.value: [
        {
            "id": "sec_tech_01",
            "topic": "Authentication vs Authorization & JWT Security",
            "question_text": "Compare Authentication with Authorization. What are common security vulnerabilities with JSON Web Tokens (JWTs), and how do you mitigate them in production?",
            "rubric_hints": [
                "AuthN (identity verification) vs AuthZ (permission enforcement)",
                "JWT risks: sensitive payload data leakage, weak signing secrets, algorithm 'none' attacks",
                "Revocation challenges and short-lived access tokens with rotating refresh tokens",
                "Storage security: HttpOnly, Secure, SameSite cookies vs localStorage"
            ],
            "default_followup": "If a user's account is compromised, how do you instantly invalidate their active JWTs before expiration without destroying system throughput?",
        },
        {
            "id": "sec_tech_02",
            "topic": "OWASP Top 10 & SQL Injection Defense",
            "question_text": "Explain how SQL Injection occurs at the database driver level. Why do parameterized queries prevent SQL injection, whereas string sanitization often fails?",
            "rubric_hints": [
                "Separation of SQL code and untrusted data in query compilation phases",
                "Prepared statements and pre-compiled query execution plans",
                "Bypassing naive regex filters with alternative character encodings or comment tricks",
                "Principle of Least Privilege for database service accounts"
            ],
            "default_followup": "Can SQL injection occur even when using an Object-Relational Mapper (ORM) like SQLAlchemy or Prisma? Give an example.",
        },
    ],
}



# Focused interview tracks use the same evaluation pipeline, with role-specific prompts.
INTERVIEW_TRACK_QUESTIONS: Dict[str, List[Dict]] = {
    InterviewType.BEHAVIORAL.value: [
        {"id":"hr_01","competency":"Introduction & Motivation","question_text":"Tell me about yourself and explain why this role is a logical next step for you.","rubric_hints":["Concise present-past-future story","Evidence linked to role","Specific motivation"],"default_followup":"Which experience best demonstrates your readiness for this role?"},
        {"id":"hr_02","competency":"Strengths & Growth","question_text":"What is one strength you rely on and one skill you are actively improving? Give a real example of each.","rubric_hints":["Specific evidence","Honest growth area","Actions taken"],"default_followup":"What observable change shows that you are improving?"},
        {"id":"hr_03","competency":"Conflict & Collaboration","question_text":"Describe a real disagreement with a teammate and how you worked toward a constructive outcome.","rubric_hints":["Respectful listening","Personal actions","Outcome and learning"],"default_followup":"What would you do if the disagreement remained unresolved?"},
        {"id":"hr_04","competency":"Failure & Learning","question_text":"Tell me about a mistake or setback you took responsibility for. What changed afterward?","rubric_hints":["Ownership","Specific correction","Learning applied later"],"default_followup":"What early signal would help you catch this sooner next time?"},
        {"id":"hr_05","competency":"Career Motivation","question_text":"Why this role and team, and what do you hope to contribute in your first six months?","rubric_hints":["Role-specific motivation","Realistic contribution","Learning goals"],"default_followup":"How would you measure progress during those six months?"},
        {"id":"hr_06","competency":"Feedback","question_text":"Describe feedback that was difficult to hear and how you responded to it.","rubric_hints":["Non-defensive response","Concrete action","Evidence of adjustment"],"default_followup":"What would the person who gave you that feedback notice today?"},
        {"id":"hr_07","competency":"Integrity & Accountability","question_text":"Tell me about a time you had to admit that you did not know something. How did you handle it?","rubric_hints":["Honesty","Proactive learning","Clear communication"],"default_followup":"How did you close the knowledge gap afterward?"},
        {"id":"hr_08","competency":"Adaptability","question_text":"Describe a time your original plan changed unexpectedly. How did you adapt?","rubric_hints":["Recognize changed constraints","Adjust priorities","Reflect on outcome"],"default_followup":"What would you do differently if the same change happened again?"},
    ],
    InterviewType.MANAGERIAL.value: [
        {"id":"mgr_01","competency":"Prioritization","question_text":"Two important deliverables are due at the same time and your team has limited capacity. How do you decide what happens first?","rubric_hints":["Impact and urgency","Explicit trade-offs","Stakeholder communication"],"default_followup":"What would make you revisit your decision?"},
        {"id":"mgr_02","competency":"Delegation","question_text":"A teammate is struggling with a task you delegated. How do you support them while keeping the work moving?","rubric_hints":["Clarify blocker","Match support to need","Ownership without blame"],"default_followup":"What would you do if the deadline still looked at risk?"},
        {"id":"mgr_03","competency":"Underperformance","question_text":"A team member repeatedly misses commitments. How would you address the issue fairly and constructively?","rubric_hints":["Private factual conversation","Understand root cause","Clear expectations and follow-up"],"default_followup":"How would you balance empathy with accountability?"},
        {"id":"mgr_04","competency":"Decision Making","question_text":"Describe a decision you made with incomplete information. How did you manage uncertainty and risk?","rubric_hints":["Assumptions stated","Alternatives considered","Reversible next step"],"default_followup":"What new evidence would cause you to change course?"},
        {"id":"mgr_05","competency":"Stakeholder Alignment","question_text":"Two stakeholders want conflicting outcomes. How would you align them and communicate a decision?","rubric_hints":["Clarify shared goals","Make trade-offs visible","Close the communication loop"],"default_followup":"What would you do if one stakeholder rejected the agreed decision?"},
        {"id":"mgr_06","competency":"Team Delivery","question_text":"Your project is behind schedule. What steps would you take in the next 24 hours and over the next week?","rubric_hints":["Diagnose before acting","Prioritize critical path","Communicate risks and recovery plan"],"default_followup":"What would you stop or defer to protect the most important outcome?"},
        {"id":"mgr_07","competency":"Coaching","question_text":"A capable teammate wants to grow but lacks confidence in a new responsibility. How would you coach them?","rubric_hints":["Ask before advising","Set a manageable stretch goal","Agree on follow-up"],"default_followup":"How would you know whether your coaching approach is helping?"},
        {"id":"mgr_08","competency":"Managing Change","question_text":"Your team resists a process change you believe is necessary. How would you build understanding and adoption?","rubric_hints":["Explain why change matters","Listen to objections","Pilot and measure"],"default_followup":"What if the pilot showed the new process was worse?"},
    ],
    InterviewType.SITUATIONAL.value: [
        {"id":"sit_01","competency":"Ethical Judgment","question_text":"You discover a serious issue just before a demo. Fixing it may delay the release. What do you do?","rubric_hints":["Assess severity","Protect users","Escalate transparently"],"default_followup":"How would you explain the decision to a stakeholder who wants to ship anyway?"},
        {"id":"sit_02","competency":"Ambiguity","question_text":"You receive a vague request with a short deadline. What do you clarify first and how do you proceed?","rubric_hints":["Clarifying questions","Explicit assumptions","Small validation step"],"default_followup":"What would you do if the stakeholder were unavailable?"},
        {"id":"sit_03","competency":"Resource Trade-offs","question_text":"You can deliver two of three requested features before launch. How do you recommend what to defer?","rubric_hints":["User impact","Risk and dependencies","Transparent trade-offs"],"default_followup":"How would you validate that the chosen priorities are correct?"},
        {"id":"sit_04","competency":"Incident Response","question_text":"A production issue affects some users, but the cause is unclear. Walk through your first actions.","rubric_hints":["Stabilize and assess impact","Use evidence and logs","Communicate and learn"],"default_followup":"What information would you include in the first status update?"},
        {"id":"sit_05","competency":"Fairness & Integrity","question_text":"A colleague asks you to present a result as successful even though the evidence is mixed. How do you respond?","rubric_hints":["Truthful reporting","Respectful challenge","Evidence-based alternative"],"default_followup":"How would you handle pressure to keep the uncertainty out of the report?"},
        {"id":"sit_06","competency":"Customer Impact","question_text":"A requested shortcut would meet the deadline but create a known usability issue. What do you recommend?","rubric_hints":["Assess affected users","Compare alternatives","Explain risk transparently"],"default_followup":"What minimum safe scope could you deliver on time?"},
        {"id":"sit_07","competency":"Conflicting Evidence","question_text":"Two data sources suggest different conclusions and a decision is due today. How do you proceed?","rubric_hints":["Check data quality","State uncertainty","Choose a reversible action if possible"],"default_followup":"How would you communicate the confidence level of your recommendation?"},
        {"id":"sit_08","competency":"Incident Learning","question_text":"A small issue repeats after a previous fix. How would you respond beyond fixing the immediate symptom?","rubric_hints":["Find root cause","Add prevention and monitoring","Share learning"],"default_followup":"How would you verify that the issue is truly resolved?"},
    ],
    InterviewType.COMMUNICATION.value: [
        {"id":"com_01","competency":"Explain Technical Work","question_text":"Explain a technical problem you solved to a non-technical manager in under two minutes.","rubric_hints":["Plain language","User or business impact","Check for understanding"],"default_followup":"How would you explain the same issue to a customer affected by it?"},
        {"id":"com_02","competency":"Communicate a Delay","question_text":"You realize a promised delivery will be late. What do you tell the stakeholder and when?","rubric_hints":["Early notice","Reason without excuses","Options and next update"],"default_followup":"What if you cannot yet estimate a reliable new delivery date?"},
        {"id":"com_03","competency":"Defend a Recommendation","question_text":"Describe how you would present a recommendation when your audience disagrees with your preferred solution.","rubric_hints":["Audience-aware framing","Evidence and alternatives","Invite challenge"],"default_followup":"What evidence would make you change your recommendation?"},
        {"id":"com_04","competency":"Active Listening","question_text":"A stakeholder says your solution misses the point. How do you respond and find the real need?","rubric_hints":["Clarify before defending","Reflect the concern","Agree on next step"],"default_followup":"How would you confirm that your revised understanding is correct?"},
        {"id":"com_05","competency":"Concise Updates","question_text":"Give a short status update for a project with progress, a blocker, a risk, and a request for help.","rubric_hints":["Clear status","Impact and owner","Specific ask"],"default_followup":"What details would you leave out for an executive audience?"},
        {"id":"com_06","competency":"Executive Summary","question_text":"Summarize a complex project for a busy decision-maker in three sentences.","rubric_hints":["Lead with outcome","Choose relevant detail","End with decision or ask"],"default_followup":"Which detail would you add if the audience asked for technical depth?"},
        {"id":"com_07","competency":"Disagree Respectfully","question_text":"How would you challenge a senior colleague's recommendation while preserving a productive working relationship?","rubric_hints":["Respectful framing","Evidence over status","Shared objective"],"default_followup":"What would you do if the decision still went against your recommendation?"},
        {"id":"com_08","competency":"Clarify Expectations","question_text":"A request is unclear and the stakeholder is impatient. How do you ask for clarification without slowing the work unnecessarily?","rubric_hints":["Concise questions","State assumptions","Confirm success criteria"],"default_followup":"What assumption would you document before proceeding?"},
    ],
}

def get_default_technical_questions() -> List[Dict]:
    """Default fallback technical questions suitable for all tech disciplines."""
    return TECHNICAL_QUESTIONS_BY_ROLE[TargetRole.SOFTWARE_ENGINEERING.value]



# Additional curated questions complete each role's technical quiz to five items.
ROLE_SPECIFIC_QUESTION_EXTENSIONS = {
    TargetRole.SOFTWARE_ENGINEERING.value: [
        ("Distributed Systems Reliability", "A service must remain available while a dependency is slow or unavailable. Design timeout, retry, circuit-breaker, and idempotency behavior, and explain how you would prevent a retry storm.", ["Timeout budgets", "Exponential backoff and jitter", "Circuit breakers and bulkheads", "Idempotency and observability"]),
    ],
    TargetRole.FRONTEND_ENGINEERING.value: [
        ("Accessible UI Architecture", "Design an accessible responsive form for keyboard and screen-reader users. How would you manage focus, validation errors, loading states, and component tests?", ["Semantic HTML", "Keyboard focus management", "Accessible validation feedback", "Responsive and automated testing"]),
        ("Browser Rendering & Async State", "A page becomes unresponsive when several network requests finish together. Explain how you would profile rendering, avoid unnecessary updates, and handle stale responses.", ["Main-thread rendering", "State colocation and memoization", "Cancellation and race prevention", "Performance measurement"]),
    ],
    TargetRole.DATA_SCIENCE_ML.value: [
        ("Feature Engineering & Leakage", "A model performs exceptionally well in validation but poorly after deployment. Investigate temporal leakage, target leakage, preprocessing, and train/serve skew.", ["Leakage diagnosis", "Time-aware validation", "Pipeline-fitted preprocessing", "Production drift monitoring"]),
        ("Model Deployment & Monitoring", "Design a production workflow for deploying a classifier whose input distribution changes over time. How would you monitor quality and decide when to retrain?", ["Reproducible artifacts", "Data and concept drift", "Delayed ground-truth metrics", "Rollback and retraining criteria"]),
    ],
    TargetRole.PRODUCT_MANAGEMENT.value: [
        ("Product Discovery & Validation", "Users request a large feature, but the underlying problem is unclear. Design a discovery plan and define evidence that would justify building or rejecting it.", ["User interviews", "Opportunity sizing", "Experiment design", "Decision criteria"]),
        ("Roadmap & Stakeholder Trade-offs", "Two senior stakeholders demand conflicting roadmap priorities while engineering capacity is fixed. How would you make and communicate the prioritization decision?", ["Outcome-based prioritization", "Dependencies and opportunity cost", "Stakeholder alignment", "Decision records"]),
        ("Experimentation & Metrics", "A product experiment increases engagement but reduces paid conversion. Explain how you would interpret the result and decide what to ship.", ["North-star and guardrail metrics", "Experiment validity", "Segment analysis", "Decision thresholds"]),
    ],
    TargetRole.DEVOPS_CLOUD.value: [
        ("Cloud Reliability & SLOs", "A cloud service meets its average latency target but frequently violates its p99 latency objective. Design an SLO and incident response approach.", ["SLI/SLO and error budgets", "Tail-latency diagnosis", "Capacity analysis", "Alert quality"]),
        ("Container Security & Supply Chain", "Design a secure CI/CD path for containerized services from source commit to production deployment.", ["Minimal reproducible images", "Dependency and image scanning", "Secret handling and provenance", "Progressive delivery and rollback"]),
        ("Infrastructure Resilience", "A region-wide cloud outage affects a critical service. Propose a recovery architecture and explain cost and consistency trade-offs.", ["RTO and RPO", "Multi-zone and multi-region design", "Replication consistency", "Failover testing"]),
    ],
    TargetRole.AI_LLM_ENGINEERING.value: [
        ("LLM Evaluation & Guardrails", "A retrieval-augmented assistant gives plausible but unsupported answers. Design an evaluation and guardrail strategy to reduce hallucinations.", ["Groundedness and retrieval recall", "Golden datasets", "Citation and abstention behavior", "Prompt-injection defenses"]),
        ("Vector Search & Retrieval Quality", "A RAG system retrieves semantically similar but irrelevant chunks. Explain how you would tune chunking, metadata filters, hybrid search, and reranking.", ["Chunk boundaries and metadata", "Dense and sparse retrieval", "Reranking and recall@k", "Latency and cost"]),
        ("LLM Serving & Cost", "An LLM application has rising latency and token costs under concurrent load. Design a serving strategy that balances quality, throughput, and cost.", ["Caching and batching", "Model routing", "Streaming and concurrency limits", "Quality-cost evaluation"]),
    ],
    TargetRole.CYBERSECURITY.value: [
        ("Incident Response & Forensics", "An organization detects unusual outbound traffic from a production host. Describe how you would contain the incident, preserve evidence, and identify the attack path.", ["Containment and evidence integrity", "Endpoint and network telemetry", "Scope and root-cause analysis", "Recovery"]),
        ("Network Segmentation & Zero Trust", "Design access controls for a hybrid environment containing employee devices, cloud workloads, and sensitive databases.", ["Identity and device posture", "Least privilege and segmentation", "Policy enforcement", "Continuous verification"]),
        ("Secure SDLC & Threat Modeling", "A new API handles sensitive customer data. Explain how you would threat-model it and integrate security checks into development.", ["Trust boundaries and abuse cases", "Authentication and authorization", "SAST/DAST and dependency checks", "Security testing"]),
    ],
}


def build_role_specific_question_bank(
    target_role: str,
    experience_level: str,
    num_questions: int = 5,
) -> List[QuestionItem]:
    """Build a technical-only quiz from the selected role's curated question pool."""
    role_key = target_role if target_role in TECHNICAL_QUESTIONS_BY_ROLE else TargetRole.SOFTWARE_ENGINEERING.value
    base_pool = list(TECHNICAL_QUESTIONS_BY_ROLE[role_key])
    extensions = ROLE_SPECIFIC_QUESTION_EXTENSIONS.get(role_key, [])
    pool = base_pool + [
        {
            "id": f"role_extension_{index + 1}",
            "topic": topic,
            "question_text": question,
            "rubric_hints": hints,
            "default_followup": f"What measurable evidence would validate your approach to {topic.lower()}?",
        }
        for index, (topic, question, hints) in enumerate(extensions)
    ]
    random.shuffle(pool)
    count = max(1, min(10, num_questions))
    if len(pool) < count:
        raise ValueError(f"The {role_key} question bank has {len(pool)} unique questions; {count} were requested.")
    return [
        QuestionItem(
            id=f"{item['id']}_{uuid.uuid4().hex[:8]}",
            category=QuestionCategory.TECHNICAL,
            role=role_key,
            question_text=item["question_text"],
            competency_or_topic=item.get("topic", "Role-specific technical knowledge"),
            rubric_hints=item.get("rubric_hints", []),
            default_followup=item.get("default_followup", ""),
        )
        for item in pool[:count]
    ]


def build_interview_plan(
    target_role: str,
    experience_level: str,
    interview_type: str,
    num_questions: int = 6,
) -> List[QuestionItem]:
    """
    Constructs a tailored, balanced question sequence (5-8 questions) based on candidate parameters.
    Ensures technical, behavioral, and project-explanation questions are covered according to interview type.
    """
    num_questions = max(5, min(8, num_questions))
    questions: List[QuestionItem] = []

    # Get role-specific technical question pool
    role_key = target_role if target_role in TECHNICAL_QUESTIONS_BY_ROLE else TargetRole.SOFTWARE_ENGINEERING.value
    tech_pool = list(TECHNICAL_QUESTIONS_BY_ROLE.get(role_key, get_default_technical_questions()))
    beh_pool = list(BEHAVIORAL_QUESTIONS)
    proj_pool = list(PROJECT_QUESTIONS)

    random.shuffle(tech_pool)
    random.shuffle(beh_pool)
    random.shuffle(proj_pool)

    # Determine mix ratios based on interview type
    if interview_type == InterviewType.BEHAVIORAL.value:
        # Heavily behavioral, with 1 project and 1 situational
        selected_beh = beh_pool[: max(3, num_questions - 2)]
        selected_proj = proj_pool[:1]
        selected_tech = tech_pool[: max(1, num_questions - len(selected_beh) - len(selected_proj))]
    elif interview_type == InterviewType.TECHNICAL.value:
        # Heavily technical, with 1-2 project architecture
        selected_tech = tech_pool[: max(3, num_questions - 2)]
        selected_proj = proj_pool[:2]
        selected_beh = beh_pool[: max(1, num_questions - len(selected_tech) - len(selected_proj))]
    elif interview_type == InterviewType.PROJECT_EXPLANATION.value:
        # Heavily project architecture & trade-offs, with supporting technical & behavioral
        selected_proj = proj_pool[: max(3, num_questions - 3)]
        selected_tech = tech_pool[:2]
        selected_beh = beh_pool[: max(1, num_questions - len(selected_proj) - len(selected_tech))]
    else:
        # Comprehensive Mixed: balanced blend of Technical, Behavioral, and Project
        # For 6 questions: 2 Behavioral, 2 Technical, 2 Project
        n_each = max(1, num_questions // 3)
        selected_beh = beh_pool[:n_each]
        selected_tech = tech_pool[:n_each]
        selected_proj = proj_pool[:num_questions - (len(selected_beh) + len(selected_tech))]

    raw_list = []
    # Interleave question categories for engaging session pacing
    max_len = max(len(selected_beh), len(selected_tech), len(selected_proj))
    for i in range(max_len):
        if i < len(selected_beh):
            raw_list.append(("beh", selected_beh[i]))
        if i < len(selected_tech):
            raw_list.append(("tech", selected_tech[i]))
        if i < len(selected_proj):
            raw_list.append(("proj", selected_proj[i]))

    # Focused HR, leadership, situational and communication tracks stay within the same scoring flow.
    focused_pool = INTERVIEW_TRACK_QUESTIONS.get(interview_type)
    if focused_pool:
        track_pool = list(focused_pool)
        random.shuffle(track_pool)
        raw_list = [("beh", item) for item in track_pool[:num_questions]]
    else:
        # Trim to exact requested count
        raw_list = raw_list[:num_questions]

    for idx, (cat_type, q_data) in enumerate(raw_list):
        if cat_type == "beh":
            category = QuestionCategory.BEHAVIORAL
            competency = q_data.get("competency", "Behavioral Competency")
        elif cat_type == "tech":
            category = QuestionCategory.TECHNICAL
            competency = q_data.get("topic", "Technical Knowledge")
        else:
            category = QuestionCategory.PROJECT
            competency = q_data.get("competency", "Project Engineering")

        item = QuestionItem(
            id=f"{q_data.get('id', f'q_{idx+1}')}",
            category=category,
            role=target_role,
            question_text=q_data["question_text"],
            competency_or_topic=competency,
            rubric_hints=q_data.get("rubric_hints", []),
            default_followup=q_data.get("default_followup", "Can you elaborate on the measurable outcome or trade-offs of your decision?"),
        )
        questions.append(item)

    return questions
