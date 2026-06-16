#!/usr/bin/env python3
"""FastAPI Backend Server for Calipr Recruiter Web Application.

Exposes REST API endpoints for candidate management, file parsing,
ranking pipeline execution, and persistent evaluation history.
"""

import os
import sys
import uuid
import json
import logging
import time
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure packages can be imported from parent path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("server")

# Import pipeline components
try:
    from pipeline.ingest import load_candidates, parse_jd_with_llm, validate_candidate, load_candidate_schema
    from pipeline.retrieval import build_faiss_index, hybrid_retrieve
    from pipeline.scoring import (
        semantic_fit_score,
        skills_match_score,
        career_trajectory_score,
        behavioral_score,
        domain_alignment_score,
        compute_final_score
    )
    from pipeline.reranker import agentic_rerank, call_llm
    from pypdf import PdfReader
except ImportError as exc:
    logger.error("Failed to import pipeline modules: %s", exc)
    sys.exit(1)

app = FastAPI(title="Calipr AI Recruiter API", version="1.0.0")

# Setup CORS to allow React Frontend (typically port 5173 or 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = current_dir / "data"
CANDIDATES_FILE = DATA_DIR / "candidates.json"
SCHEMA_FILE = DATA_DIR / "candidate_schema.json"
HISTORY_FILE = DATA_DIR / "history.json"
MAP_FILE = DATA_DIR / "skill_adjacency_map.json"

# Ensure data dir exists
DATA_DIR.mkdir(parents=True, exist_ok=True)
if not HISTORY_FILE.exists():
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

# Global variables for models
_embed_model = None

def get_embedding_model():
    global _embed_model
    if _embed_model is not None:
        return _embed_model
    try:
        from sentence_transformers import SentenceTransformer
        model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        logger.info("Loading sentence-transformers: %s", model_name)
        _embed_model = SentenceTransformer(model_name)
    except Exception as e:
        logger.warning("Failed to load sentence-transformers: %s. Using fallback mock embeddings.", e)
        _embed_model = None
    return _embed_model

def generate_fallback_embedding(text: str) -> List[float]:
    import hashlib
    import numpy as np
    h = hashlib.sha256(text.encode('utf-8')).digest()
    rng = np.random.default_rng(int.from_bytes(h[:4], 'big'))
    vec = rng.normal(0.0, 1.0, 384).tolist()
    norm = sum(x*x for x in vec) ** 0.5
    if norm == 0:
        return [0.0] * 384
    return [x / norm for x in vec]

def parse_resume_text_with_llm(resume_text: str, provider: str = "groq") -> Dict[str, Any]:
    """Use LLM to extract structured fields from candidate resume text."""
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
        f"Resume text:\n{resume_text}"
    )
    
    api_key_env = "GROQ_API_KEY" if provider == "groq" else "GEMINI_API_KEY"
    api_key = os.getenv(api_key_env)
    
    if not api_key:
        logger.warning("%s not set. Using fallback regex resume parsing.", api_key_env)
        return generate_mock_parsed_resume(resume_text)
        
    try:
        response = call_llm(prompt, provider=provider)
        # Strip code fences if returned
        if response.strip().startswith("```"):
            response = re.sub(r"^```(?:json)?\s*\n?", "", response.strip(), flags=re.MULTILINE)
            response = re.sub(r"\n?```\s*$", "", response, flags=re.MULTILINE)
        parsed = json.loads(response.strip())
        return parsed
    except Exception as e:
        logger.error("LLM resume parsing failed: %s. Falling back to mock.", e)
        return generate_mock_parsed_resume(resume_text)

def generate_mock_parsed_resume(text: str) -> Dict[str, Any]:
    """Basic fallback parser for resumes."""
    # Find email
    import re
    emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    email = emails[0] if emails else "contact@candidate.com"
    
    # Try to guess name from first line
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    name = lines[0] if lines else "New Candidate"
    if len(name) > 30:
        name = "New Candidate"
        
    return {
        "name": name,
        "email": email,
        "current_title": "Software Engineer",
        "years_experience": 3,
        "skills": ["Python", "JavaScript", "SQL", "Git"],
        "domains": ["Web Development", "AI/ML"],
        "behavioral_signals": {
            "profile_completeness": 0.85,
            "response_speed_hours": 24.0,
            "portfolio_depth": 0.75
        },
        "career_progression": [
            {
                "title": "Software Engineer",
                "company": "Tech Corp",
                "duration_months": 36
            }
        ]
    }

class ConfigModel(BaseModel):
    groq_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    llm_provider: Optional[str] = "groq"

# --- API ENDPOINTS ---

@app.get("/api/candidates")
def get_all_candidates():
    """Retrieve all candidates from candidates.json."""
    if not CANDIDATES_FILE.exists():
        return []
    try:
        with open(CANDIDATES_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read candidates database: {e}")

@app.post("/api/candidates/upload")
def upload_candidate_resume(
    file: UploadFile = File(...),
    provider: str = Form("groq")
):
    """Upload a candidate resume (PDF or TXT) and parse it into candidates.json."""
    filename = file.filename
    
    try:
        # Extract text
        if filename.endswith(".pdf"):
            reader = PdfReader(file.file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
        else:
            text = file.file.read().decode("utf-8")
            
        if not text.strip():
            raise HTTPException(status_code=400, detail="Uploaded file is empty or text extraction failed.")
            
        # Parse text into candidate schema using LLM
        parsed_profile = parse_resume_text_with_llm(text, provider=provider)
        
        # Add internal fields
        cid = str(uuid.uuid4())
        parsed_profile["candidate_id"] = cid
        parsed_profile["resume_text"] = text
        parsed_profile["created_at"] = datetime.utcnow().isoformat()
        
        # Generate embedding
        embed_model = get_embedding_model()
        if embed_model:
            parsed_profile["resume_embedding"] = embed_model.encode(text).tolist()
        else:
            parsed_profile["resume_embedding"] = generate_fallback_embedding(text)
            
        # Validate against schema
        if SCHEMA_FILE.exists():
            schema = load_candidate_schema(str(SCHEMA_FILE))
            is_valid, errors = validate_candidate(parsed_profile, schema)
            if not is_valid:
                logger.warning("Uploaded candidate failed schema checks: %s", errors)
                # We can still proceed but warn in logging
        
        # Append to candidates.json
        candidates = []
        if CANDIDATES_FILE.exists():
            with open(CANDIDATES_FILE, "r", encoding="utf-8") as fh:
                try:
                    candidates = json.load(fh)
                except Exception:
                    candidates = []
                    
        candidates.append(parsed_profile)
        with open(CANDIDATES_FILE, "w", encoding="utf-8") as fh:
            json.dump(candidates, fh, indent=2)
            
        logger.info("Successfully added candidate %s via resume upload.", parsed_profile.get("name"))
        return parsed_profile
        
    except Exception as e:
        logger.error("Failed to upload and parse candidate resume: %s", e)
        raise HTTPException(status_code=500, detail=f"Failed to process resume: {e}")

@app.post("/api/candidates/manual")
def add_candidate_manual(candidate_data: Dict[str, Any]):
    """Manually add a candidate via JSON editor."""
    try:
        # Ensure ID exists
        if "candidate_id" not in candidate_data and "id" not in candidate_data:
            candidate_data["candidate_id"] = str(uuid.uuid4())
        elif "candidate_id" not in candidate_data:
            candidate_data["candidate_id"] = candidate_data["id"]
            
        if "resume_text" not in candidate_data or not candidate_data["resume_text"]:
            # Reconstruct dummy resume text from skills/title for search
            skills_str = ", ".join(candidate_data.get("skills", []))
            candidate_data["resume_text"] = f"{candidate_data.get('name', '')} is a {candidate_data.get('current_title', '')} with skills in {skills_str}."

        # Generate embedding
        embed_model = get_embedding_model()
        resume_text = candidate_data["resume_text"]
        if embed_model:
            candidate_data["resume_embedding"] = embed_model.encode(resume_text).tolist()
        else:
            candidate_data["resume_embedding"] = generate_fallback_embedding(resume_text)
            
        candidate_data["created_at"] = datetime.utcnow().isoformat()
        
        # Validate against schema
        if SCHEMA_FILE.exists():
            schema = load_candidate_schema(str(SCHEMA_FILE))
            is_valid, errors = validate_candidate(candidate_data, schema)
            if not is_valid:
                raise HTTPException(status_code=400, detail=f"Schema validation failed: {errors}")
                
        # Append
        candidates = []
        if CANDIDATES_FILE.exists():
            with open(CANDIDATES_FILE, "r", encoding="utf-8") as fh:
                try:
                    candidates = json.load(fh)
                except Exception:
                    candidates = []
                    
        candidates.append(candidate_data)
        with open(CANDIDATES_FILE, "w", encoding="utf-8") as fh:
            json.dump(candidates, fh, indent=2)
            
        return candidate_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save candidate: {e}")

class RunPipelineRequest(BaseModel):
    jd_text: str
    min_years: int = 0
    provider: str = "groq"

@app.post("/api/pipeline/run")
def run_recruitment_pipeline(req: RunPipelineRequest):
    """Execute Calipr AI 5-Signal scoring and ranking for a job description."""
    start_time = time.time()
    
    if not CANDIDATES_FILE.exists() or os.path.getsize(CANDIDATES_FILE) == 0:
        raise HTTPException(status_code=400, detail="Candidates database is empty. Please upload or add candidates first.")
        
    try:
        # Load candidate pool
        with open(CANDIDATES_FILE, "r", encoding="utf-8") as fh:
            candidates = json.load(fh)
            
        logger.info("Starting pipeline run. Candidates pool size: %d", len(candidates))
        
        # 1. Decode JD
        jd = parse_jd_with_llm(req.jd_text, provider=req.provider)
        # Apply override filter if specified
        min_years = max(req.min_years, jd.get("min_years", 0))
        
        # Pre-filter by experience
        filtered_candidates = [c for c in candidates if c.get("years_experience", 0) >= min_years]
        logger.info("Candidates meeting experience threshold (%d yrs): %d", min_years, len(filtered_candidates))
        
        if not filtered_candidates:
            return {
                "run_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "jd_summary": jd,
                "candidates_ranked": 0,
                "shortlist": []
            }
            
        # 2. Get embeddings
        embed_model = get_embedding_model()
        jd_query_text = f"{jd.get('title', '')} {jd.get('domain', '')} " + " ".join(jd.get('required_skills', [])) + f" {jd.get('summary', '')}"
        
        if embed_model:
            jd_embedding = embed_model.encode(jd_query_text).tolist()
        else:
            jd_embedding = generate_fallback_embedding(jd_query_text)
            
        # Ensure all candidate embeddings exist
        for c in filtered_candidates:
            if "resume_embedding" not in c or not c["resume_embedding"]:
                resume_text = c.get("resume_text", "")
                if embed_model:
                    c["resume_embedding"] = embed_model.encode(resume_text).tolist()
                else:
                    c["resume_embedding"] = generate_fallback_embedding(resume_text)
                    
        # Load skill map
        adjacency_map = {}
        if MAP_FILE.exists():
            with open(MAP_FILE, "r", encoding="utf-8") as fh:
                adjacency_map = json.load(fh)
                
        # 3. Hybrid Retrieval
        embeddings = [c["resume_embedding"] for c in filtered_candidates]
        corpus = [c.get("resume_text", "") for c in filtered_candidates]
        faiss_index = build_faiss_index(embeddings)
        
        retrieved_tuples = hybrid_retrieve(
            faiss_index=faiss_index,
            query_embedding=jd_embedding,
            corpus=corpus,
            query_text=jd_query_text,
            k=min(20, len(filtered_candidates))
        )
        
        retrieved_candidates = []
        for doc_id, fused_score in retrieved_tuples:
            cand = filtered_candidates[doc_id]
            cand["retrieval_fused_score"] = fused_score
            retrieved_candidates.append(cand)
            
        # 4. 5-Signal Scoring
        for c in retrieved_candidates:
            s1 = semantic_fit_score(jd_embedding, c["resume_embedding"])
            s2 = skills_match_score(jd.get("required_skills", []), c.get("skills", []), adjacency_map)
            s3 = career_trajectory_score(c)
            s4 = behavioral_score(c)
            s5 = domain_alignment_score(jd.get("domain", ""), c.get("domains", []))
            
            scores = {
                "semantic": s1,
                "skills": s2,
                "trajectory": s3,
                "behavioral": s4,
                "domain": s5
            }
            
            c["composite_score"] = compute_final_score(scores)
            c["signal_breakdown"] = scores
            
        # Sort
        retrieved_candidates.sort(key=lambda x: x["composite_score"], reverse=True)
        top_10 = retrieved_candidates[:10]
        
        # 5. Agentic Re-Ranking
        api_key_env = "GROQ_API_KEY" if req.provider == "groq" else "GEMINI_API_KEY"
        api_key = os.getenv(api_key_env)
        
        if not api_key:
            logger.warning("No API key. Falling back to Phase 3 ranking.")
            ranked_shortlist = [
                {
                    "candidate_id": c.get("candidate_id") or c.get("id"),
                    "rank": idx + 1,
                    "rationale": f"Ranked by 5-signal composite score (semantic={c['signal_breakdown']['semantic']:.2f}, skills={c['signal_breakdown']['skills']:.2f}). API key not set."
                }
                for idx, c in enumerate(top_10)
            ]
        else:
            jd_summary = jd.get("summary", "")
            ranked_shortlist = agentic_rerank(
                jd_summary=jd_summary,
                candidates=top_10,
                provider=req.provider
            )
            
        # Format response shortlist
        response_shortlist = []
        cand_map = {c.get("candidate_id") or c.get("id"): c for c in top_10}
        
        for item in ranked_shortlist:
            cid = item["candidate_id"]
            rank = item["rank"]
            rationale = item["rationale"]
            
            c = cand_map.get(cid, {})
            response_shortlist.append({
                "candidate_id": cid,
                "name": c.get("name", "N/A"),
                "email": c.get("email", "N/A"),
                "current_title": c.get("current_title", "N/A"),
                "years_experience": c.get("years_experience", 0),
                "composite_score": c.get("composite_score", 0.0),
                "signal_breakdown": c.get("signal_breakdown", {}),
                "skills": c.get("skills", []),
                "rank": rank,
                "rationale": rationale
            })
            
        run_id = str(uuid.uuid4())
        run_record = {
            "run_id": run_id,
            "timestamp": datetime.utcnow().isoformat(),
            "jd_text": req.jd_text,
            "jd_summary": jd,
            "min_years": min_years,
            "candidates_ranked": len(response_shortlist),
            "shortlist": response_shortlist,
            "duration_seconds": time.time() - start_time
        }
        
        # Save run context to history.json
        history = []
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, "r", encoding="utf-8") as fh:
                try:
                    history = json.load(fh)
                except Exception:
                    history = []
        
        history.insert(0, run_record)  # Save newest first
        with open(HISTORY_FILE, "w", encoding="utf-8") as fh:
            json.dump(history, fh, indent=2)
            
        return run_record
        
    except Exception as e:
        logger.error("Error executing ranking pipeline: %s", e)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to execute pipeline: {e}")

@app.get("/api/history")
def get_run_history():
    """Retrieve history of runs."""
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read history: {e}")

@app.get("/api/config")
def get_llm_config():
    """Get active configuration settings, with masked API keys for security."""
    return {
        "groq_api_key": "****" if os.getenv("GROQ_API_KEY") else "",
        "gemini_api_key": "****" if os.getenv("GEMINI_API_KEY") else "",
        "llm_provider": os.getenv("LLM_PROVIDER", "groq")
    }

@app.post("/api/config")
def update_llm_config(conf: ConfigModel):
    """Update configurations and save them persistently to .env."""
    env_path = current_dir / ".env"
    
    # Load existing env definitions
    lines = []
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
    env_map = {}
    for line in lines:
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            env_map[k.strip()] = v.strip()
            
    # Update map
    if conf.groq_api_key is not None:
        env_map["GROQ_API_KEY"] = conf.groq_api_key
        os.environ["GROQ_API_KEY"] = conf.groq_api_key
    if conf.gemini_api_key is not None:
        env_map["GEMINI_API_KEY"] = conf.gemini_api_key
        os.environ["GEMINI_API_KEY"] = conf.gemini_api_key
    if conf.llm_provider is not None:
        env_map["LLM_PROVIDER"] = conf.llm_provider
        os.environ["LLM_PROVIDER"] = conf.llm_provider
        
    # Write back to .env
    with open(env_path, "w", encoding="utf-8") as f:
        for k, v in env_map.items():
            f.write(f"{k}={v}\n")
            
    return {"status": "success", "provider": os.getenv("LLM_PROVIDER")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
