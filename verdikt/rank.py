#!/usr/bin/env python3
"""
Verdikt Ranker — Fully offline. No API calls. CPU only.
Usage: python rank.py --candidates candidates.jsonl --out submission.csv
"""
import os
import argparse
import json
import csv
import numpy as np
from datetime import date
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import re
import time

# ── CONFIG ────────────────────────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K_BM25 = 8000       # Pre-filter: BM25 top-8000 before embedding (improved recall safety)
TOP_K_FINAL = 100       # Output top 100

# Signal weights
W_SEMANTIC   = 0.30
W_SKILLS     = 0.25
W_CAREER     = 0.20
W_BEHAVIORAL = 0.15
W_DOMAIN     = 0.10

# JD-extracted values (from pre-computation step)
JD_CORE_SKILLS = []      # Filled by parse_jd()
JD_ADJACENT    = []
JD_DOMAIN_KW   = []
JD_MIN_EXP     = 0

SKILL_ADJACENCY = {
    "python": ["julia","r","scala","cython","cpython","micropython","jython","pypy"],
    "pytorch": ["tensorflow","jax","keras","mxnet","torch"],
    "react": ["vue","angular","svelte","next.js","react.js","redux"],
    "fastapi": ["flask","django","express","pydantic","uvicorn"],
    "postgresql": ["mysql","sqlite","mongodb","postgres","sql","supabase","cockroachdb"],
    "docker": ["kubernetes","podman","containerization","docker-compose","containerd"],
    "aws": ["gcp","azure","digitalocean","amazon web services","ec2","s3","lambda"],
    "langchain": ["llamaindex","haystack","autogen"],
    "bert": ["roberta","distilbert","gpt-2","t5"],
    "yolov8": ["yolov5","detectron2","efficientdet"],
}

try:
    adj_path = "skill_adjacency_map.json"
    if os.path.exists(adj_path):
        with open(adj_path, encoding="utf-8") as f:
            custom_adj = json.load(f)
            for k, v in custom_adj.items():
                k_lower = k.lower().strip()
                v_lowers = [item.lower().strip() for item in v]
                if k_lower in SKILL_ADJACENCY:
                    SKILL_ADJACENCY[k_lower] = list(set(SKILL_ADJACENCY[k_lower] + v_lowers))
                else:
                    SKILL_ADJACENCY[k_lower] = v_lowers
except Exception as e:
    print(f"[WARN] Could not load skill_adjacency_map.json: {e}")

LEVEL_MAP = {
    "intern":0.10,"trainee":0.12,"junior":0.20,"associate":0.28,
    "mid":0.40,"engineer":0.40,"developer":0.40,"analyst":0.35,
    "senior":0.70,"lead":0.82,"staff":0.88,"principal":0.93,
    "architect":0.90,"director":0.93,"manager":0.72,"head":0.85,
    "vp":0.95,"cto":1.0,"founder":0.88
}

LEVEL_ORDER = [
    "cto", "vp", "director", "architect", "principal", "staff", "lead", "senior",
    "intern", "trainee", "junior", "associate", "founder", "manager", "head",
    "mid", "engineer", "developer", "analyst"
]

SIZE_MAP = {"1-10":1,"11-50":2,"51-200":3,"201-500":4,
            "501-1000":5,"1001-5000":6,"5001-10000":7,"10001+":8}

# ── TEXT UTILS ────────────────────────────────────────────────────
def build_candidate_text(c):
    p = c.get('profile', {})
    skills_text = " ".join([s.get('name') or '' for s in c.get('skills', [])])
    career_text = " ".join([jh.get('description') or '' for jh in c.get('career_history', [])])
    titles_text = " ".join([jh.get('title') or '' for jh in c.get('career_history', [])])
    full_text = f"{p.get('summary') or ''} {p.get('headline') or ''} {p.get('current_title') or ''} {skills_text} {career_text} {titles_text}"
    # Truncate to first 300 words to speed up CPU encoding (model max length is 256 tokens)
    words = full_text.split()
    if len(words) > 300:
        return " ".join(words[:300])
    return full_text

def tokenize(text):
    STOP = {"a","an","the","and","or","in","on","at","to","for","of","with","is","are","was","were","i","we","you"}
    return [t for t in re.findall(r'\b[a-z0-9][a-z0-9+#\.]*\b', text.lower()) if t not in STOP and len(t) > 1]

def is_non_tech_candidate(c, jd_core, jd_adjacent):
    p = c.get('profile', {})
    title = (p.get('current_title') or '').lower().strip()
    if not title:
        return False
        
    NON_TECH_ROLES = [
        "marketing", "sales", "recruiter", "talent acquisition", "human resources",
        "accountant", "bookkeeper", "clerk", "content writer", "copywriter", 
        "business development", "bde", "customer support", "customer success", 
        "receptionist", "operations executive", "social media manager", 
        "brand executive", "store manager", "lawyer", "legal", "doctor", "nurse", "teacher",
        "chef", "cashier", "waiter", "hostess", "hr"
    ]
    
    TECH_KEYWORDS = {
        "software", "data", "machine learning", "ml", "nlp", "ai", "artificial intelligence", 
        "deep learning", "computer vision", "backend", "frontend", "fullstack", "full stack", 
        "cloud", "devops", "systems", "infrastructure", "platform", "algorithm", "researcher", 
        "scientist", "quantitative", "analyst", "database", "network", "web", "application", 
        "programmer", "technical", "engineering", "technology", "information retrieval", "search"
    }
    
    # Tokenize title
    title_words = set(re.findall(r'\b[a-z0-9+#\.]+\b', title))
    has_tech_keyword = any(kw in title_words or kw in title for kw in TECH_KEYWORDS)
    
    # Get candidate skills
    cand_skills = [(s.get('name') or '').lower().strip() for s in c.get('skills', [])]
    
    GENERAL_TECH_SKILLS = {
        "python", "pytorch", "tensorflow", "keras", "scikit-learn", "numpy", "pandas",
        "sql", "nosql", "postgres", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
        "opensearch", "faiss", "milvus", "qdrant", "pinecone", "weaviate", "chroma",
        "java", "c++", "c#", "javascript", "typescript", "react", "node", "docker", "kubernetes",
        "aws", "gcp", "azure", "git", "linux", "c", "go", "golang", "rust", "scala", "spark", "hadoop",
        "machine learning", "deep learning", "artificial intelligence", "nlp", "computer vision",
        "neural networks", "llm", "llms", "bert", "gpt", "transformers", "embeddings", "vector database"
    }
    all_tech_skills = set(s.lower().strip() for s in jd_core + jd_adjacent).union(GENERAL_TECH_SKILLS)
    
    has_tech_skill = any(any(ts in cs or cs in ts for ts in all_tech_skills) for cs in cand_skills)
    
    # 1. Check if the title is explicitly non-tech and does not contain tech keywords
    for role in NON_TECH_ROLES:
        if re.search(r'\b' + re.escape(role) + r'\b', title):
            if not has_tech_keyword:
                return True
                
    # 2. If title contains "engineer" but has zero ML/tech skills and no tech keywords
    if "engineer" in title:
        if not has_tech_keyword and not has_tech_skill:
            return True
            
    # 3. Explicitly drop background engineering roles if they have no tech skills
    BACKGROUND_ENGINEERS = ["civil", "mechanical", "chemical", "construction", "industrial", "environmental", "aerospace", "materials"]
    for bg in BACKGROUND_ENGINEERS:
        if bg in title and "engineer" in title:
            if not has_tech_skill:
                return True
                
    return False

# ── SIGNALS ───────────────────────────────────────────────────────
def sig_semantic(emb_candidate, emb_jd):
    dot = np.dot(emb_candidate, emb_jd)
    norms = np.linalg.norm(emb_candidate) * np.linalg.norm(emb_jd)
    return float(dot / norms) if norms > 0 else 0.0

def sig_skills(candidate_skills, assessment_scores):
    if not JD_CORE_SKILLS:
        return 0.5
    PROF = {'beginner':0.4,'intermediate':0.6,'advanced':0.85,'expert':1.0}
    cand_map = {(s.get('name') or '').lower().strip(): s for s in candidate_skills if s.get('name')}
    score = 0.0
    
    # Case-insensitive assessment scores
    asmnt_map = {k.lower().strip(): v for k, v in (assessment_scores or {}).items()}
    
    for jd_skill in JD_CORE_SKILLS:
        jl = jd_skill.lower().strip()
        if jl in cand_map:
            s = cand_map[jl]
            asmnt_val = asmnt_map.get(jl, 0)
            if asmnt_val >= 70:
                base = 1.0
            else:
                base = PROF.get(s.get('proficiency','intermediate'), 0.6)
            dur  = min(s.get('duration_months',0)/24, 1.0) * 0.15
            asmnt = (asmnt_val / 100) * 0.10
            score += min(base + dur + asmnt, 1.0)
        else:
            adj_list = SKILL_ADJACENCY.get(jl, [])
            if any(a.lower().strip() in cand_map for a in adj_list):
                score += 0.40
    return min(score / max(len(JD_CORE_SKILLS), 1), 1.0)

def sig_career(c):
    p = c.get('profile', {})
    career = c.get('career_history', [])
    edu = c.get('education', [])
    
    # Title precedence seniority lookup
    title = (p.get('current_title') or '').lower()
    seniority = 0.35
    for k in LEVEL_ORDER:
        if k in title:
            seniority = LEVEL_MAP[k]
            break
            
    # Normalized experience depth (15 year cap)
    years = float(p.get('years_of_experience') or 0.0)
    exp_score = min(years / 15.0, 1.0)
            
    # Chronological progression from oldest to newest company size
    sizes = [SIZE_MAP.get(jh.get('company_size','1-10'), 1) for jh in career]
    prog = max((sizes[0] - sizes[-1]) / 7, 0.0) if len(sizes) > 1 else 0.0
    
    tier_bonus = {'tier_1':0.15,'tier_2':0.10,'tier_3':0.05,'tier_4':0.0,'unknown':0.02}
    best_tier = max((tier_bonus.get(e.get('tier','unknown'),0.02) for e in edu), default=0.02)
    
    # Blended Trajectory score
    score = min(seniority*0.40 + exp_score*0.20 + prog*0.20 + best_tier*0.20, 1.0)
    
    # Consulting company penalty
    curr_company = (p.get('current_company') or '').lower()
    consulting_firms = ["tcs", "tata consultancy services", "infosys", "wipro", "cognizant",
                        "accenture", "capgemini", "tech mahindra", "hcl", "hcltech", "l&t", "lnt", "mindtree"]
    if any(comp in curr_company for comp in consulting_firms):
        score *= 0.85
        
    return score

def sig_behavioral(rs):
    if not rs:
        rs = {}
    try:
        last_active = date.fromisoformat((rs.get('last_active_date') or '').split('T')[0])
        days_ago = (date.today() - last_active).days
    except Exception:
        days_ago = 30
    freshness = max(0.0, 1.0 - days_ago/90)
    
    completeness_val = rs.get('profile_completeness_score')
    completeness = (80 if completeness_val is None else completeness_val)/100
    
    response_rate = rs.get('recruiter_response_rate')
    if response_rate is None:
        response_rate = 0.5
        
    resp_time_val = rs.get('avg_response_time_hours')
    resp_time_val = 24 if resp_time_val is None else resp_time_val
    resp_time  = max(0, 1 - resp_time_val/72)
    
    interview = rs.get('interview_completion_rate')
    if interview is None:
        interview = 0.5
        
    engagement = response_rate*0.4 + resp_time*0.3 + interview*0.3
    
    gh = rs.get('github_activity_score')
    github = 0.3 if (gh is None or gh == -1) else gh/100
    
    offer = rs.get('offer_acceptance_rate')
    offer_n = 0.5 if (offer is None or offer == -1) else max(offer, 0)
    
    # Notice Period Score (10% weight)
    notice = rs.get('notice_period_days')
    if notice is None:
        notice = 30
    try:
        notice = float(notice)
    except Exception:
        notice = 30
    notice_score = max(0.0, 1.0 - (notice / 180))
    
    # Open To Work Internal Weight (5% weight)
    otw = 1.0 if rs.get('open_to_work_flag', False) else 0.3
    
    # Verified indicators (5% weight)
    verified = (int(rs.get('verified_email', False)) + int(rs.get('verified_phone', False)) + int(rs.get('linkedin_connected', False)))/3
    
    # Relocation or Remote Work Mode Bonus (+0.05)
    relocate = rs.get('willing_to_relocate', False)
    work_mode = (rs.get('preferred_work_mode') or '').lower()
    bonus = 0.0
    if relocate or work_mode == "remote" or work_mode == "hybrid":
        bonus = 0.05
        
    score = (
        completeness * 0.18 +
        freshness * 0.12 +
        engagement * 0.25 +
        github * 0.15 +
        offer_n * 0.10 +
        notice_score * 0.10 +
        otw * 0.05 +
        verified * 0.05
    ) + bonus
    
    return min(score, 1.0)

def sig_domain(c):
    if not JD_DOMAIN_KW:
        return 0.5
    p = c.get('profile', {})
    industries = [p.get('current_industry') or ''] + [jh.get('industry') or '' for jh in c.get('career_history',[])]
    industries = [ind for ind in industries if ind]
    text = ((p.get('summary') or '') + ' ' + (p.get('headline') or '') + ' ' + ' '.join(industries)).lower()
    hits = sum(1 for kw in JD_DOMAIN_KW if kw.lower() in text)
    return min(hits / max(len(JD_DOMAIN_KW), 1), 1.0)

def compute_score(c, emb_c, emb_jd):
    rs = c.get('redrob_signals', {})
    s1 = sig_semantic(emb_c, emb_jd)
    s2 = sig_skills(c.get('skills',[]), rs.get('skill_assessment_scores',{}))
    s3 = sig_career(c)
    s4 = sig_behavioral(rs)
    s5 = sig_domain(c)
    final = s1*W_SEMANTIC + s2*W_SKILLS + s3*W_CAREER + s4*W_BEHAVIORAL + s5*W_DOMAIN
    
    # Post-fusion OTW multiplier
    if not rs.get('open_to_work_flag', False):
        final *= 0.75
        
    return round(final, 4), s1, s2, s3, s4, s5

def generate_reasoning(c, s2_skills):
    p = c.get('profile', {})
    rs = c.get('redrob_signals', {})
    
    current_title = p.get('current_title', 'Software Engineer')
    if not current_title:
        current_title = 'Software Engineer'
    
    # Ensure current_title is strictly printable ASCII and truncated to keep under 120 chars total
    current_title = "".join(ch for ch in current_title if 32 <= ord(ch) <= 126)
    if len(current_title) > 40:
        current_title = current_title[:37] + "..."
        
    try:
        years_experience = int(float(p.get('years_of_experience', 0)))
    except Exception:
        years_experience = 0
    
    # Count core skills matched explicitly
    candidate_skills = {s.get('name', '').lower().strip() for s in c.get('skills', [])}
    matched_core_skills = 0
    for jd_skill in JD_CORE_SKILLS:
        jl = jd_skill.lower().strip()
        if any(jl == cs or jl in cs or cs in jl for cs in candidate_skills):
            matched_core_skills += 1
            
    recruiter_response_rate = rs.get('recruiter_response_rate', 0.0)
    if recruiter_response_rate is None:
        recruiter_response_rate = 0.0
    try:
        recruiter_response_rate = float(recruiter_response_rate)
    except Exception:
        recruiter_response_rate = 0.0
        
    return f"{current_title} with {years_experience} yrs; {matched_core_skills} core skills matched; response rate {recruiter_response_rate:.2f}."

# ── MAIN PIPELINE ─────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    
    t0 = time.time()
    print("Loading model...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    
    # Load JD (pre-computed or from docx)
    print("Loading JD embedding...")
    try:
        emb_jd = np.load("jd_embedding.npy")
    except FileNotFoundError:
        from docx import Document
        doc = Document("job_description.docx")
        jd_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        emb_jd = model.encode(jd_text)
        np.save("jd_embedding.npy", emb_jd)
    
    # Load JD skills (from jd_skills.json if exists)
    try:
        with open("jd_skills.json", encoding="utf-8") as f:
            jd_config = json.load(f)
            JD_CORE_SKILLS.extend(jd_config.get("core_skills", []))
            JD_ADJACENT.extend(jd_config.get("adjacent_skills", []))
            JD_DOMAIN_KW.extend(jd_config.get("domain_keywords", []))
    except FileNotFoundError:
        print("[WARN] jd_skills.json not found. Skills scoring will be approximate.")
    
    # ── PHASE 1: Title Pre-filter + BM25 Pre-filter ─────────────
    print("Phase 1: Pre-filtering...")
    candidates_raw = []
    corpus_tokens  = []
    
    # Query strictly from JD core skills to keep sparse search domain-specific
    jd_query = tokenize(" ".join(JD_CORE_SKILLS))
    
    # Stream the dataset line-by-line to build the BM25 corpus in memory (RAM safe)
    with open(args.candidates, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            c = json.loads(line)
            
            # String match pre-filter: drop non-tech titles and invalid engineering backgrounds
            if is_non_tech_candidate(c, JD_CORE_SKILLS, JD_ADJACENT):
                continue
                
            candidates_raw.append(c)
            corpus_tokens.append(tokenize(build_candidate_text(c)))
    
    print(f"  Loaded {len(candidates_raw):,} candidates after title pre-filter")
    
    if jd_query and len(corpus_tokens) > 0:
        bm25 = BM25Okapi(corpus_tokens)
        bm25_scores = bm25.get_scores(jd_query)
        top_indices = np.argsort(bm25_scores)[-TOP_K_BM25:][::-1]
        candidates_filtered = [candidates_raw[i] for i in top_indices]
    else:
        candidates_filtered = candidates_raw[:TOP_K_BM25]
    
    print(f"  After BM25 filter: {len(candidates_filtered):,} candidates")
    
    # ── PHASE 2: Embed + Score ──────────────────────────────────
    print("Phase 2: Embedding + scoring...")
    texts = [build_candidate_text(c) for c in candidates_filtered]
    embeddings = model.encode(texts, batch_size=256, show_progress_bar=True)
    
    scored = []
    for i, c in enumerate(candidates_filtered):
        final, s1, s2, s3, s4, s5 = compute_score(c, embeddings[i], emb_jd)
        scored.append({
            "candidate_id": c["candidate_id"],
            "score": final,
            "s2": s2,
            "reasoning": generate_reasoning(c, s2),
            "_c": c
        })
    
    # ── PHASE 3: Sort + Top 100 ─────────────────────────────────
    scored.sort(key=lambda x: (-x["score"], x["candidate_id"]))
    top100 = scored[:TOP_K_FINAL]
    
    # Create output directory if it doesn't exist
    out_dir = os.path.dirname(args.out)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
        
    # ── PHASE 4: Write CSV ──────────────────────────────────────
    with open(args.out, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for rank, row in enumerate(top100, 1):
            # Format score to 4 decimal places matching requirements
            writer.writerow([row["candidate_id"], rank, f"{row['score']:.4f}", row["reasoning"]])
    
    elapsed = round(time.time() - t0, 1)
    print(f"\n[DONE] Done in {elapsed}s -> {args.out}")
    print(f"Top 3: {[(r['candidate_id'], f'{r['score']:.4f}') for r in top100[:3]]}")

if __name__ == "__main__":
    main()
