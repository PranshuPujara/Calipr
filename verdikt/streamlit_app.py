import streamlit as st
import json
import numpy as np
from datetime import date
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import re
from docx import Document
import pandas as pd

# Safe import of PdfReader
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

# Initialize session state for custom uploaded candidates
if "uploaded_candidates" not in st.session_state:
    st.session_state.uploaded_candidates = []

st.set_page_config(
    page_title="Calipr AI - Redrob Ranker Sandbox",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CONFIG & CONSTANTS ────────────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LEVEL_MAP = {
    "intern":0.10,"trainee":0.12,"junior":0.20,"associate":0.28,
    "mid":0.40,"engineer":0.40,"developer":0.40,"analyst":0.35,
    "senior":0.70,"lead":0.82,"staff":0.88,"principal":0.93,
    "architect":0.90,"director":0.93,"manager":0.72,"head":0.85,
    "vp":0.95,"cto":1.0,"founder":0.88
}
SIZE_MAP = {"1-10":1,"11-50":2,"51-200":3,"201-500":4,
            "501-1000":5,"1001-5000":6,"5001-10000":7,"10001+":8}
SKILL_ADJACENCY = {
    "Python": ["Julia","R","Scala"],
    "PyTorch": ["TensorFlow","JAX","Keras","MXNet"],
    "React": ["Vue","Angular","Svelte","Next.js"],
    "FastAPI": ["Flask","Django","Express"],
    "PostgreSQL": ["MySQL","SQLite","MongoDB"],
    "Docker": ["Kubernetes","Podman"],
    "AWS": ["GCP","Azure","DigitalOcean"],
    "LangChain": ["LlamaIndex","Haystack","AutoGen"],
    "BERT": ["RoBERTa","DistilBERT","GPT-2","T5"],
    "YOLOv8": ["YOLOv5","Detectron2","EfficientDet"],
}

# ── CACHED MODEL LOADERS ──────────────────────────────────────────
@st.cache_resource
def load_sentence_transformer():
    return SentenceTransformer(EMBEDDING_MODEL)

@st.cache_data
def load_sample_candidates():
    with open("sample_candidates.json", "r", encoding="utf-8") as f:
        return json.load(f)

# ── MATH & SCORING UTILS ──────────────────────────────────────────
def build_candidate_text(c):
    p = c.get('profile', {})
    skills_text = " ".join([s.get('name','') for s in c.get('skills', [])])
    career_text = " ".join([jh.get('description','') for jh in c.get('career_history', [])])
    titles_text = " ".join([jh.get('title','') for jh in c.get('career_history', [])])
    return f"{p.get('summary','')} {p.get('headline','')} {p.get('current_title','')} {skills_text} {career_text} {titles_text}"

def tokenize(text):
    STOP = {"a","an","the","and","or","in","on","at","to","for","of","with","is","are","was","were","i","we","you"}
    return [t for t in re.findall(r'\b[a-z0-9][a-z0-9+#\.]*\b', text.lower()) if t not in STOP and len(t) > 1]

def sig_semantic(emb_candidate, emb_jd):
    dot = np.dot(emb_candidate, emb_jd)
    norms = np.linalg.norm(emb_candidate) * np.linalg.norm(emb_jd)
    return float(dot / norms) if norms > 0 else 0.0

def sig_skills(candidate_skills, assessment_scores, core_skills):
    if not core_skills:
        return 0.5
    PROF = {'beginner':0.4,'intermediate':0.6,'advanced':0.85,'expert':1.0}
    cand_map = {s.get('name','').lower(): s for s in candidate_skills}
    score = 0.0
    for jd_skill in core_skills:
        jl = jd_skill.lower()
        matched_s = None
        for s in candidate_skills:
            sn = s.get('name','').lower()
            if sn == jl or sn in jl or jl in sn:
                matched_s = s
                break
        if matched_s:
            s = matched_s
            base = PROF.get(s.get('proficiency','intermediate'), 0.6)
            dur  = min(s.get('duration_months',0)/24, 1.0) * 0.15
            asmnt= (assessment_scores.get(s.get('name'), 0)/100) * 0.10
            score += min(base + dur + asmnt, 1.0)
        else:
            adj_list = SKILL_ADJACENCY.get(jd_skill, [])
            if any(a.lower() in cand_map for a in adj_list):
                score += 0.40
    return min(score / max(len(core_skills), 1), 1.0)

def sig_career(c):
    p = c.get('profile', {})
    career = c.get('career_history', [])
    edu = c.get('education', [])
    title = p.get('current_title','').lower()
    seniority = next((v for k,v in LEVEL_MAP.items() if k in title), 0.35)
    sizes = [SIZE_MAP.get(jh.get('company_size','1-10'), 1) for jh in career]
    prog = max((sizes[-1]-sizes[0])/7, 0.0) if len(sizes) > 1 else 0.0
    tier_bonus = {'tier_1':0.15,'tier_2':0.10,'tier_3':0.05,'tier_4':0.0,'unknown':0.02}
    best_tier = max((tier_bonus.get(e.get('tier','unknown'),0.02) for e in edu), default=0.02)
    return min(seniority*0.50 + prog*0.30 + best_tier*0.20, 1.0)

def sig_behavioral(rs):
    try:
        last_active = date.fromisoformat(rs.get('last_active_date', '').split('T')[0])
        days_ago = (date.today() - last_active).days
    except Exception:
        days_ago = 30
    freshness  = max(0.0, 1.0 - days_ago/90)
    completeness = rs.get('profile_completeness_score', 80)/100
    response_rate = rs.get('recruiter_response_rate', 0.5)
    resp_time  = max(0, 1 - rs.get('avg_response_time_hours', 24)/72)
    interview  = rs.get('interview_completion_rate', 0.5)
    engagement = response_rate*0.4 + resp_time*0.3 + interview*0.3
    gh = rs.get('github_activity_score', -1)
    github = 0.3 if gh == -1 else gh/100
    offer = rs.get('offer_acceptance_rate', -1)
    offer_n = 0.5 if offer == -1 else max(offer, 0)
    otw = 1.0 if rs.get('open_to_work_flag', False) else 0.3
    verified = (int(rs.get('verified_email', False)) + int(rs.get('verified_phone', False)) + int(rs.get('linkedin_connected', False)))/3
    saved = min(rs.get('saved_by_recruiters_30d', 0)/10, 1.0)
    return min(
        completeness*0.18 + freshness*0.15 + engagement*0.25 +
        github*0.15 + offer_n*0.10 + otw*0.05 + verified*0.07 + saved*0.05, 1.0
    )

def sig_domain(c, domain_kws):
    if not domain_kws:
        return 0.5
    p = c.get('profile', {})
    industries = [p.get('current_industry','')] + [jh.get('industry','') for jh in c.get('career_history',[])]
    text = (p.get('summary','') + ' ' + p.get('headline','') + ' ' + ' '.join(industries)).lower()
    hits = sum(1 for kw in domain_kws if kw.lower() in text)
    return min(hits / max(len(domain_kws), 1), 1.0)

def generate_reasoning(c, s2_skills, core_skills):
    p = c.get('profile', {})
    rs = c.get('redrob_signals', {})
    matched = round(s2_skills * max(len(core_skills), 1))
    return (f"{p.get('current_title', 'Developer')} with {p.get('years_of_experience', 0)} yrs; "
            f"{matched} core skills matched; "
            f"response rate {rs.get('recruiter_response_rate', 0.0):.2f}.")

def extract_text_from_file(uploaded_file):
    filename = uploaded_file.name
    if filename.endswith(".pdf"):
        if PdfReader is None:
            return "Error: pypdf library is not installed."
        try:
            reader = PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            return f"Error reading PDF: {e}"
    elif filename.endswith(".docx"):
        try:
            doc = Document(uploaded_file)
            return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        except Exception as e:
            return f"Error reading DOCX: {e}"
    else:
        try:
            return uploaded_file.read().decode("utf-8", errors="ignore")
        except Exception as e:
            return f"Error reading text file: {e}"

def parse_resume_offline(text, filename="Resume"):
    emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    email = emails[0] if emails else "contact@candidate.com"
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    name = lines[0] if lines else filename.split('.')[0]
    if len(name) > 30:
        name = filename.split('.')[0]
        
    exp_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(?:years|yrs|year)\b', text.lower())
    years_exp = float(exp_matches[0]) if exp_matches else 3.0
    if years_exp > 40:
        years_exp = 3.0
        
    known_skills = [
        "Python", "PyTorch", "React", "FastAPI", "PostgreSQL", "Docker", "AWS", "LangChain", "BERT", "YOLOv8",
        "JavaScript", "TypeScript", "HTML", "CSS", "SQL", "Git", "Spark", "Kafka", "TensorFlow", "Kubernetes",
        "C++", "Java", "Go", "Rust", "Node.js", "MongoDB", "Redis", "Framer", "Figma", "Tailwind"
    ]
    detected_skills = []
    for skill in known_skills:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text.lower()):
            detected_skills.append({
                "name": skill,
                "proficiency": "advanced" if skill in ["Python", "JavaScript", "SQL"] else "intermediate",
                "duration_months": int(years_exp * 6)
            })
            
    title = "Software Engineer"
    titles = ["backend engineer", "frontend engineer", "fullstack engineer", "full stack engineer",
              "data scientist", "data engineer", "machine learning engineer", "devops engineer",
              "software engineer", "product manager", "ui/ux designer"]
    for t in titles:
        if t in text.lower():
            title = t.title()
            break
            
    import uuid
    cid = f"UPLOAD_{uuid.uuid4().hex[:7].upper()}"
    
    candidate = {
        "candidate_id": cid,
        "profile": {
            "anonymized_name": name,
            "headline": f"{title} | {', '.join([s['name'] for s in detected_skills[:3]])}",
            "summary": text[:300] + ("..." if len(text) > 300 else ""),
            "location": "Remote",
            "country": "Global",
            "years_of_experience": years_exp,
            "current_title": title,
            "current_company": "Independent Consultant",
            "current_company_size": "1-10",
            "current_industry": "Tech"
        },
        "career_history": [
            {
                "company": "Current Company",
                "title": title,
                "duration_months": int(years_exp * 12),
                "is_current": True,
                "company_size": "1-10",
                "description": f"Worked as {title} utilizing skills like {', '.join([s['name'] for s in detected_skills[:5]])}."
            }
        ],
        "education": [
            {
                "institution": "University",
                "degree": "Bachelor of Science",
                "field_of_study": "Computer Science",
                "start_year": 2018,
                "end_year": 2022,
                "tier": "tier_2"
            }
        ],
        "skills": detected_skills,
        "redrob_signals": {
            "skill_assessment_scores": {s["name"]: 85 for s in detected_skills},
            "profile_completeness_score": 90,
            "recruiter_response_rate": 0.85,
            "avg_response_time_hours": 12.0,
            "interview_completion_rate": 0.90,
            "github_activity_score": 80,
            "offer_acceptance_rate": 0.80,
            "open_to_work_flag": True,
            "verified_email": True,
            "verified_phone": True,
            "linkedin_connected": True,
            "saved_by_recruiters_30d": 3,
            "last_active_date": date.today().isoformat()
        }
    }
    return candidate

def parse_resume_with_groq(text, groq_key):
    try:
        from groq import Groq
        client = Groq(api_key=groq_key)
        prompt = (
            "Extract structured candidate details from the resume below. "
            "Return ONLY a JSON object that matches this format (no markdown code blocks, no other text):\n"
            "{\n"
            "  \"name\": \"Candidate Full Name\",\n"
            "  \"email\": \"candidate@email.com\",\n"
            "  \"current_title\": \"Job Title\",\n"
            "  \"years_experience\": integer,\n"
            "  \"skills\": [\"Skill1\", \"Skill2\", ...],\n"
            "  \"domains\": [\"Domain1\", \"Domain2\", ...],\n"
            "  \"behavioral_signals\": {\n"
            "    \"profile_completeness\": float (0.0 to 1.0),\n"
            "    \"response_speed_hours\": float (e.g. 12.5),\n"
            "    \"portfolio_depth\": float (0.0 to 1.0)\n"
            "  },\n"
            "  \"career_progression\": [\n"
            "    {\n"
            "      \"title\": \"Title\",\n"
            "      \"company\": \"Company\",\n"
            "      \"duration_months\": integer\n"
            "    }\n"
            "  ]\n"
            "}\n\n"
            f"Resume text:\n{text}"
        )
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=2048,
        )
        response_text = response.choices[0].message.content or ""
        if response_text.strip().startswith("```"):
            response_text = re.sub(r"^```(?:json)?\s*\n?", "", response_text.strip(), flags=re.MULTILINE)
            response_text = re.sub(r"\n?```\s*$", "", response_text, flags=re.MULTILINE)
        parsed = json.loads(response_text.strip())
        
        import uuid
        cid = f"UPLOAD_{uuid.uuid4().hex[:7].upper()}"
        detected_skills = [{
            "name": s,
            "proficiency": "advanced",
            "duration_months": int(parsed.get("years_experience", 3) * 12)
        } for s in parsed.get("skills", [])]
        
        candidate = {
            "candidate_id": cid,
            "profile": {
                "anonymized_name": parsed.get("name", "New Candidate"),
                "headline": f"{parsed.get('current_title', 'Developer')} | {', '.join(parsed.get('skills', [])[:3])}",
                "summary": text[:300] + ("..." if len(text) > 300 else ""),
                "location": "Remote",
                "country": "Global",
                "years_of_experience": float(parsed.get("years_experience", 3)),
                "current_title": parsed.get("current_title", "Software Engineer"),
                "current_company": parsed.get("career_progression", [{}])[0].get("company", "Independent Consultant") if parsed.get("career_progression") else "Independent Consultant",
                "current_company_size": "1-10",
                "current_industry": parsed.get("domains", ["Tech"])[0] if parsed.get("domains") else "Tech"
            },
            "career_history": [
                {
                    "company": job.get("company", "Company"),
                    "title": job.get("title", "Developer"),
                    "duration_months": job.get("duration_months", 12),
                    "is_current": i == 0,
                    "company_size": "1-10",
                    "description": f"Worked as {job.get('title')} at {job.get('company')}."
                } for i, job in enumerate(parsed.get("career_progression", []))
            ],
            "education": [
                {
                    "institution": "University",
                    "degree": "Bachelor's Degree",
                    "field_of_study": "Computer Science",
                    "start_year": 2018,
                    "end_year": 2022,
                    "tier": "tier_2"
                }
            ],
            "skills": detected_skills,
            "redrob_signals": {
                "skill_assessment_scores": {s["name"]: int(parsed.get("behavioral_signals", {}).get("profile_completeness", 0.8) * 100) for s in detected_skills},
                "profile_completeness_score": int(parsed.get("behavioral_signals", {}).get("profile_completeness", 0.8) * 100),
                "recruiter_response_rate": 0.85,
                "avg_response_time_hours": parsed.get("behavioral_signals", {}).get("response_speed_hours", 12.0),
                "interview_completion_rate": 0.90,
                "github_activity_score": int(parsed.get("behavioral_signals", {}).get("portfolio_depth", 0.75) * 100),
                "offer_acceptance_rate": 0.80,
                "open_to_work_flag": True,
                "verified_email": True,
                "verified_phone": True,
                "linkedin_connected": True,
                "saved_by_recruiters_30d": 3,
                "last_active_date": date.today().isoformat()
            }
        }
        return candidate
    except Exception as e:
        st.warning(f"Groq LLM parsing failed: {e}. Falling back to offline rule-based parser.")
        return parse_resume_offline(text, filename="Resume")

# ── STREAMLIT INTERFACE ───────────────────────────────────────────
st.title("🏆 Calipr AI — Redrob Ranker Sandbox")
st.markdown("This interactive sandbox demonstrates the offline candidate ranking pipeline built for the Redrob Hackathon. It evaluates candidates from the sample pool against your job description using a 5-Signal scoring system.")

# Sidebar - Settings & Weights
st.sidebar.header("🛠️ Pipeline Weights")
w_semantic = st.sidebar.slider("Signal 1: Semantic Fit", 0.0, 1.0, 0.30, 0.05)
w_skills = st.sidebar.slider("Signal 2: Skills Match", 0.0, 1.0, 0.25, 0.05)
w_career = st.sidebar.slider("Signal 3: Career Trajectory", 0.0, 1.0, 0.20, 0.05)
w_behavioral = st.sidebar.slider("Signal 4: Behavioral Signals", 0.0, 1.0, 0.15, 0.05)
w_domain = st.sidebar.slider("Signal 5: Domain Alignment", 0.0, 1.0, 0.10, 0.05)

# Normalize weights
total_weight = w_semantic + w_skills + w_career + w_behavioral + w_domain
if abs(total_weight - 1.0) > 0.01:
    st.sidebar.warning(f"Weights sum to {total_weight:.2f}. They will be normalized to 1.0 automatically.")

# Sidebar - LLM Parser Config
st.sidebar.markdown("---")
st.sidebar.header("🔑 LLM Configuration")
groq_key_input = st.sidebar.text_input("Groq API Key (Optional)", type="password", help="Enter Groq API Key to parse resumes with LLM. Otherwise, offline rule-based parsing is used.")

# Sidebar - Resume Uploader
st.sidebar.markdown("---")
st.sidebar.header("📄 Upload Candidate Resumes")
uploaded_resumes = st.sidebar.file_uploader("Upload resumes (PDF, TXT, or DOCX)", type=["pdf", "txt", "docx"], accept_multiple_files=True)

# Parse uploaded resumes
if uploaded_resumes:
    new_candidates_added = False
    for f in uploaded_resumes:
        # Check if we've already parsed this file name to avoid duplicate parsing
        if f.name not in [c.get("_filename") for c in st.session_state.uploaded_candidates]:
            with st.spinner(f"Parsing {f.name}..."):
                text = extract_text_from_file(f)
                if text and not text.startswith("Error"):
                    if groq_key_input:
                        cand = parse_resume_with_groq(text, groq_key_input)
                    else:
                        cand = parse_resume_offline(text, filename=f.name)
                    cand["_filename"] = f.name
                    st.session_state.uploaded_candidates.append(cand)
                    new_candidates_added = True
                else:
                    st.sidebar.error(f"Failed to read {f.name}: {text}")
    if new_candidates_added:
        st.sidebar.success(f"Added {len(uploaded_resumes)} custom candidate(s)!")

# Show number of custom candidates
if st.session_state.uploaded_candidates:
    st.sidebar.info(f"Custom Candidates Uploaded: {len(st.session_state.uploaded_candidates)}")
    if st.sidebar.button("🗑️ Clear Uploaded Candidates"):
        st.session_state.uploaded_candidates = []
        st.rerun()

# Main sections
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Job Description Input")
    jd_input_method = st.radio("Choose input method", ["Use Default Hackathon JD", "Paste custom JD text", "Upload job_description.docx"])
    
    jd_text = ""
    if jd_input_method == "Use Default Hackathon JD":
        try:
            doc = Document("job_description.docx")
            jd_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        except Exception:
            jd_text = "Senior Backend Engineer with experience in hybrid search, vector databases, Python, and ranking algorithms."
        st.text_area("Default Job Description Text (read-only)", jd_text, height=250, disabled=True)
    elif jd_input_method == "Paste custom JD text":
        jd_text = st.text_area("Paste Job Description here", height=250)
    else:
        uploaded_file = st.file_uploader("Upload Job Description (DOCX, PDF, or TXT)", type=["docx", "pdf", "txt"])
        if uploaded_file:
            filename = uploaded_file.name
            if filename.endswith(".docx"):
                doc = Document(uploaded_file)
                jd_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            elif filename.endswith(".pdf"):
                if PdfReader is None:
                    jd_text = "Error: pypdf is not installed."
                else:
                    reader = PdfReader(uploaded_file)
                    jd_text = ""
                    for page in reader.pages:
                        jd_text += page.extract_text() or ""
            else:
                jd_text = uploaded_file.read().decode("utf-8", errors="ignore")
            st.text_area("Extracted JD Text", jd_text, height=200, disabled=True)

with col2:
    st.subheader("🎯 Extracted Skills Config")
    st.markdown("Set the core skills and domain keywords to evaluate candidate profiles. These are parsed from the JD during precompute.")
    
    # Load default parsed skills
    default_core = ["Python", "Embeddings", "Vector Databases", "Retrieval Systems", "Ranking Systems"]
    default_adj = ["Docker", "AWS", "FAISS", "LangChain"]
    default_domain = ["AI", "ML", "Search", "NLP", "HR-tech"]
    
    try:
        with open("jd_skills.json", "r", encoding="utf-8") as f:
            jd_config = json.load(f)
            default_core = jd_config.get("core_skills", default_core)
            default_adj = jd_config.get("adjacent_skills", default_adj)
            default_domain = jd_config.get("domain_keywords", default_domain)
    except Exception:
        pass

    core_skills_str = st.text_input("Core Skills (comma-separated)", ", ".join(default_core))
    adjacent_skills_str = st.text_input("Adjacent Skills (comma-separated)", ", ".join(default_adj))
    domain_kws_str = st.text_input("Domain Keywords (comma-separated)", ", ".join(default_domain))
    
    core_skills = [s.strip() for s in core_skills_str.split(",") if s.strip()]
    adjacent_skills = [s.strip() for s in adjacent_skills_str.split(",") if s.strip()]
    domain_kws = [s.strip() for s in domain_kws_str.split(",") if s.strip()]

run_pipeline = st.button("🚀 Run Pipeline Evaluator", type="primary", use_container_width=True)

if run_pipeline:
    if not jd_text.strip():
        st.error("Please provide or upload a Job Description first.")
    else:
        with st.spinner("Initializing models and loading sample candidate pool..."):
            model = load_sentence_transformer()
            candidates = load_sample_candidates()
            # Append custom candidates
            if st.session_state.uploaded_candidates:
                candidates = st.session_state.uploaded_candidates + candidates
            
        st.info(f"Successfully loaded {len(candidates)} candidate(s) (including {len(st.session_state.uploaded_candidates)} custom uploads).")
        
        # Normalize weights
        factor = 1.0 / total_weight if total_weight > 0 else 1.0
        n_semantic = w_semantic * factor
        n_skills = w_skills * factor
        n_career = w_career * factor
        n_behavioral = w_behavioral * factor
        n_domain = w_domain * factor
        
        with st.spinner("Phase 1: Computing Semantic Embeddings locally..."):
            emb_jd = model.encode(jd_text)
            candidate_texts = [build_candidate_text(c) for c in candidates]
            emb_candidates = model.encode(candidate_texts, show_progress_bar=False)
            
        with st.spinner("Phase 2: Calculating Multi-Signal Scores..."):
            scored_list = []
            for i, c in enumerate(candidates):
                rs = c.get('redrob_signals', {})
                s1 = sig_semantic(emb_candidates[i], emb_jd)
                s2 = sig_skills(c.get('skills', []), rs.get('skill_assessment_scores', {}), core_skills)
                s3 = sig_career(c)
                s4 = sig_behavioral(rs)
                s5 = sig_domain(c, domain_kws)
                
                final_score = (s1 * n_semantic) + (s2 * n_skills) + (s3 * n_career) + (s4 * n_behavioral) + (s5 * n_domain)
                reasoning = generate_reasoning(c, s2, core_skills)
                
                scored_list.append({
                    "candidate_id": c["candidate_id"],
                    "name": c.get("profile", {}).get("anonymized_name", "Anonymized"),
                    "title": c.get("profile", {}).get("current_title", "Developer"),
                    "experience": c.get("profile", {}).get("years_of_experience", 0),
                    "score": round(final_score, 4),
                    "s1_sem": round(s1, 4),
                    "s2_skl": round(s2, 4),
                    "s3_car": round(s3, 4),
                    "s4_beh": round(s4, 4),
                    "s5_dom": round(s5, 4),
                    "reasoning": reasoning,
                    "_profile": c
                })
                
            # Sort by highest score
            scored_list.sort(key=lambda x: (-x["score"], x["candidate_id"]))
            
        st.success("Evaluation complete! Showing the Top Shortlisted Candidates:")
        
        # Display table
        df_display = pd.DataFrame(scored_list)
        df_table = df_display[["candidate_id", "name", "title", "experience", "score", "reasoning"]].copy()
        df_table.insert(0, "Rank", range(1, len(df_table) + 1))
        
        st.dataframe(df_table, use_container_width=True, hide_index=True)
        
        # Detailed inspector
        st.markdown("---")
        st.subheader("🔍 Shortlist Deep-Dive Inspector")
        inspect_cand = st.selectbox(
            "Select a candidate to review detailed signal scores and profile details:",
            options=scored_list,
            format_func=lambda x: f"Rank {scored_list.index(x)+1}: {x['name']} ({x['title']}) — Score: {x['score']}"
        )
        
        if inspect_cand:
            pcol1, pcol2 = st.columns([1, 1])
            
            with pcol1:
                st.markdown(f"### 👤 {inspect_cand['name']}")
                st.markdown(f"**Current Title**: `{inspect_cand['title']}`")
                st.markdown(f"**Total Experience**: `{inspect_cand['experience']} years`")
                st.markdown(f"**Location**: {inspect_cand['_profile'].get('profile', {}).get('location', 'Unknown')}")
                st.markdown(f"**Core Reason**: *\"{inspect_cand['reasoning']}\"*")
                
                st.markdown("#### 🛠️ Signal Breakdowns")
                st.metric(label="Signal 1: Semantic Fit Score", value=inspect_cand["s1_sem"])
                st.metric(label="Signal 2: Skills Match Score", value=inspect_cand["s2_skl"])
                st.metric(label="Signal 3: Career Progression Score", value=inspect_cand["s3_car"])
                st.metric(label="Signal 4: Behavioral Score", value=inspect_cand["s4_beh"])
                st.metric(label="Signal 5: Domain Fit Score", value=inspect_cand["s5_dom"])
                
            with pcol2:
                st.markdown("### 📄 Candidate Profile Data")
                
                # Skills tab
                st.markdown("**Skills List**")
                skills_df = pd.DataFrame(inspect_cand["_profile"].get("skills", []))
                if not skills_df.empty:
                    st.dataframe(skills_df[["name", "proficiency", "duration_months"]], use_container_width=True, hide_index=True)
                else:
                    st.write("No skills found.")
                
                # Career History
                st.markdown("**Career History**")
                history = inspect_cand["_profile"].get("career_history", [])
                for job in history:
                    st.markdown(f"- **{job.get('title')}** at {job.get('company')} ({job.get('duration_months', 0)} months)")
                    st.caption(job.get('description', ''))
