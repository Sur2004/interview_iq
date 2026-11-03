"""InterviewIQ Daily Briefing — interview drills + live developer intelligence."""
from datetime import date
import html
import requests
import streamlit as st

st.set_page_config(page_title="InterviewIQ | Daily Briefing", page_icon="🗞️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
.block-container{max-width:1280px;padding-top:1.5rem;padding-bottom:3rem}
.hero{padding:30px 34px;border-radius:22px;background:radial-gradient(circle at 88% 0%,#536fe8 0,transparent 32%),linear-gradient(120deg,#101a35,#243f82 70%,#3159ba);color:#fff;margin-bottom:22px}
.hero .eyebrow{font-size:.72rem;letter-spacing:.15em;font-weight:800;color:#b9ceff}
.hero h1{color:white;font-size:2.35rem;letter-spacing:-.05em;margin:.4rem 0}
.hero p{color:#dbe5ff;margin:0;max-width:760px}
.source{font-size:.72rem;color:#667085;font-weight:700;letter-spacing:.06em;text-transform:uppercase}
.story{border:1px solid #e5eaf3;border-radius:15px;padding:17px 18px;margin:10px 0;background:linear-gradient(145deg,#fff,#f8faff)}
.story h4{font-size:1rem;line-height:1.4;margin:.35rem 0;color:#172033}
.story p{font-size:.85rem;color:#64748b;margin:.2rem 0}
.spec{border:1px solid #e5eaf3;border-radius:14px;padding:16px;margin:8px 0;background:#fff}
[data-testid="stMetric"]{border:1px solid #e5eaf3;border-radius:14px;padding:13px;background:#fff}
div.stButton>button{border-radius:10px;font-weight:700}
</style>
""", unsafe_allow_html=True)

st.markdown(f'<div class="hero"><div class="eyebrow">INTERVIEWIQ · DAILY INTELLIGENCE</div><h1>Today's interview & tech briefing</h1><p>Build interview readiness while staying current with engineering, AI and open-source releases.</p></div>', unsafe_allow_html=True)
today = date.today()
st.caption(f"DAILY EDITION · {today.strftime('%A, %d %B %Y')} · Feeds refresh every 30 minutes")

QUESTIONS = [
    ("Python", "What is the difference between a list, tuple and set in Python?", "Explain ordering, mutability, uniqueness and typical use cases.", "Use a list for ordered mutable collections, tuple for fixed records and set for unique membership checks. Mention average O(1) membership for hashable set elements."),
    ("SQL", "Given an Employee table, how would you find the second-highest distinct salary?", "Think about duplicates, ordering and NULL values.", "One portable pattern is SELECT MAX(salary) FROM Employee WHERE salary < (SELECT MAX(salary) FROM Employee). For the Nth value, use DENSE_RANK over salary descending."),
    ("Data structures", "When would you choose a hash map over a balanced binary search tree?", "Compare lookup, ordering, worst-case behaviour and memory.", "Hash maps provide expected O(1) lookup but do not maintain order. Balanced trees provide O(log n) search/insert/delete and ordered traversal."),
    ("Operating systems", "What happens during a context switch, and why does it have a cost?", "Mention CPU state, scheduler, caches and address spaces.", "The OS saves the current process/thread state, selects another runnable task and restores its state. Register and scheduling work plus cache/TLB disruption add overhead."),
    ("Computer networks", "Explain the TCP three-way handshake and why it uses three steps.", "Describe SYN, SYN-ACK, ACK and sequence number synchronisation.", "The client sends SYN, server replies SYN-ACK, client sends ACK. Both sides establish initial sequence numbers and confirm bidirectional reachability."),
    ("DBMS", "What is the difference between a clustered index and a non-clustered index?", "Explain physical organisation and index-to-row lookup.", "A clustered index determines row storage order in systems that support it; a non-clustered index stores keys and row locators separately. Exact implementation varies by database."),
    ("Machine learning", "Explain overfitting and give three ways to reduce it.", "Think generalisation, validation and model complexity.", "Overfitting learns noise in training data. Use regularisation, cross-validation, early stopping, data augmentation or simpler models; compare train and validation performance."),
    ("Cybersecurity", "What is the difference between authentication and authorisation?", "Use a real application example.", "Authentication verifies identity; authorisation decides what an authenticated identity can access. Login proves who you are; role permissions determine what you may do."),
    ("System design", "How would you design a URL shortener that handles high read traffic?", "Discuss API, ID generation, storage, cache, redirects and abuse.", "Generate collision-safe short IDs, store mappings in a durable key-value store, cache hot keys, use 301/302 deliberately, add rate limits and analytics asynchronously."),
    ("OOP", "Explain dependency injection and why it improves testability.", "Describe supplying dependencies rather than constructing them internally.", "A class receives collaborators from outside, often through its constructor. Tests can inject fakes/mocks, reducing tight coupling and making behaviour easier to isolate."),
    ("Algorithms", "What is the time complexity of binary search, and what precondition does it require?", "Explain halving the search space.", "Binary search is O(log n) time and O(1) iterative auxiliary space; the collection must be sorted and support efficient indexed access for the usual array bound."),
    ("Cloud", "What is the difference between horizontal and vertical scaling?", "Give an example and one trade-off for each.", "Vertical scaling adds resources to one machine; horizontal scaling adds machines/instances. Horizontal scaling improves capacity and resilience but needs distribution and coordination."),
    ("Generative AI", "What is retrieval-augmented generation (RAG), and when is it useful?", "Explain retrieval, context injection and generation.", "RAG retrieves relevant external documents and supplies them as context to a model. It helps ground answers in private or current knowledge and can provide source citations."),
    ("Behavioural", "Tell me about a time you had to debug a difficult issue under a deadline.", "Use Situation, Task, Action, Result. Be specific about your contribution.", "Set context briefly, define your responsibility, explain the diagnostic steps and trade-offs you personally took, then quantify the result and what you learned."),
]
question = QUESTIONS[(today.toordinal() // 1) % len(QUESTIONS)]
role = st.selectbox("Choose a practice focus", ["All roles", "Software Engineer", "Data Analyst", "Python Developer", "Cybersecurity", "AI / ML Engineer"])
role_question_indices = {
    "All roles": list(range(len(QUESTIONS))),
    "Software Engineer": [2, 3, 4, 5, 8, 9, 10],
    "Data Analyst": [1, 6, 2, 11, 12],
    "Python Developer": [0, 1, 2, 9, 10],
    "Cybersecurity": [7, 4, 3, 8],
    "AI / ML Engineer": [6, 12, 0, 2, 8],
}
eligible_questions = role_question_indices[role]
question = QUESTIONS[eligible_questions[today.toordinal() % len(eligible_questions)]]
st.subheader("Question of the day")
q1,q2 = st.columns([1.55,1], gap="large")
with q1:
    st.markdown(f"**{question[0]} · {question[1]}**")
    st.caption("Try answering aloud in 90–120 seconds before revealing the guidance.")
    answer = st.text_area("Your answer (optional self-practice)", height=150, placeholder="Structure your answer with a definition, explanation, example and trade-off…")
    with st.expander("Reveal answer structure"):
        st.write(question[2])
        st.info(question[3])
    if answer.strip():
        st.caption(f"Your draft: {len(answer.split())} words · Aim for a clear, evidence-based answer.")
with q2:
    st.markdown("#### A simple answer framework")
    st.markdown("1. **Define** the concept in one sentence.\n2. **Explain** how it works.\n3. **Example** from code or a real system.\n4. **Trade-off** or limitation.\n5. **Conclude** with when you would use it.")
    st.markdown("#### Daily target")
    st.metric("Focused practice", "20 minutes")
    st.caption("Answer the question, review the guidance, then practise one follow-up aloud.")

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_hacker_news():
    base = "https://hacker-news.firebaseio.com/v0"
    ids = requests.get(f"{base}/topstories.json", timeout=12).json()[:12]
    stories = []
    for item_id in ids[:7]:
        try:
            item = requests.get(f"{base}/item/{item_id}.json", timeout=10).json()
            if item and item.get("title"):
                stories.append({"title": item["title"], "url": item.get("url") or f"https://news.ycombinator.com/item?id={item_id}", "score": item.get("score", 0), "comments": item.get("descendants", 0), "by": item.get("by", "community")})
        except (requests.RequestException, ValueError, TypeError):
            continue
    return stories

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_devto():
    response = requests.get("https://dev.to/api/articles", params={"tag": "ai", "top": 7, "per_page": 6}, headers={"User-Agent":"InterviewIQ-DailyBriefing/1.0"}, timeout=15)
    response.raise_for_status()
    return [{"title": x.get("title","Untitled"), "url": x.get("url","https://dev.to"), "description": x.get("description","") or "", "tags": x.get("tag_list",[]), "reading_time": x.get("reading_time_minutes")} for x in response.json()[:6]]

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_github_releases():
    repos = ["ollama/ollama", "pytorch/pytorch", "huggingface/transformers", "microsoft/vscode"]
    results = []
    for repo in repos:
        try:
            response = requests.get(f"https://api.github.com/repos/{repo}/releases/latest", headers={"Accept":"application/vnd.github+json","User-Agent":"InterviewIQ-DailyBriefing/1.0"}, timeout=12)
            if response.status_code == 404:
                continue
            response.raise_for_status()
            x = response.json()
            results.append({"repo":repo,"name":x.get("name") or x.get("tag_name") or "Latest release","tag":x.get("tag_name",""),"url":x.get("html_url",""),"published":(x.get("published_at") or "")[:10],"notes":(x.get("body") or "").strip()[:1100]})
        except (requests.RequestException, ValueError, TypeError):
            continue
    return results

if st.button("↻ Refresh live feeds", type="primary"):
    fetch_hacker_news.clear()
    fetch_devto.clear()
    fetch_github_releases.clear()
    st.rerun()

st.divider()
st.subheader("Engineering pulse")
st.caption("Community-curated technology discussions from the Hacker News public API.")
try:
    with st.spinner("Loading current discussions…"):
        hn = fetch_hacker_news()
    if hn:
        for item in hn:
            st.markdown(f'<div class="story"><div class="source">HACKER NEWS · {item["score"]} points · {item["comments"]} comments</div><h4><a href="{html.escape(item["url"], quote=True)}" target="_blank">{html.escape(item["title"])}</a></h4><p>Shared by {html.escape(item["by"])}</p></div>', unsafe_allow_html=True)
    else:
        st.info("No Hacker News stories were returned. Try refreshing.")
except Exception as exc:
    st.warning(f"Could not load Hacker News right now ({type(exc).__name__}). The interview practice section remains available.")

st.divider()
st.subheader("AI & developer reading")
st.caption("Recent community articles from Dev.to's public API. Article content and opinions belong to their authors.")
try:
    with st.spinner("Loading developer articles…"):
        articles = fetch_devto()
    if articles:
        for item in articles:
            tags = " · ".join(item["tags"][:4])
            st.markdown(f'<div class="story"><div class="source">DEV.TO · {item["reading_time"] or "?"} MIN READ · {html.escape(tags)}</div><h4><a href="{html.escape(item["url"], quote=True)}" target="_blank">{html.escape(item["title"])}</a></h4><p>{html.escape(item["description"][:260])}</p></div>', unsafe_allow_html=True)
    else:
        st.info("No articles were returned. Try refreshing.")
except Exception as exc:
    st.warning(f"Could not load Dev.to articles right now ({type(exc).__name__}).")

st.divider()
st.subheader("Latest tool releases & specifications")
st.caption("Release tags and publication dates come from official GitHub release endpoints. Check linked release notes for complete specifications and compatibility.")
try:
    with st.spinner("Checking official release feeds…"):
        releases = fetch_github_releases()
    if releases:
        for item in releases:
            st.markdown(f'<div class="spec"><div class="source">{html.escape(item["repo"])} · {html.escape(item["published"] or "date not supplied")}</div><h4>{html.escape(item["name"])} <span style="color:#64748b;font-size:.82rem">{html.escape(item["tag"])}</span></h4><p>{html.escape(item["notes"][:650]) if item["notes"] else "No release summary supplied. Open the official release page for full details."}</p><a href="{html.escape(item["url"], quote=True)}" target="_blank">Official release notes ↗</a></div>', unsafe_allow_html=True)
    else:
        st.info("Release feeds returned no latest releases. Check the official project pages.")
except Exception as exc:
    st.warning(f"Could not load release specifications right now ({type(exc).__name__}).")

st.caption("Sources: Hacker News public API · Dev.to public API · GitHub Releases API. Feeds are cached for 30 minutes. Availability and ordering depend on the source APIs; this is not a real-time breaking-news service.")
