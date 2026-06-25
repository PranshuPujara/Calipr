---
title: Calipr AI
emoji: 🏆
colorFrom: indigo
colorTo: purple
sdk: streamlit
sdk_version: 1.38.0
app_file: app.py
pinned: false
---

# Calipr AI — Redrob Candidate Discovery & Ranking Sandbox

Calipr AI (powered by the Verdikt Offline Ranker) is a candidate discovery, scoring, and ranking platform built for the Redrob Intelligent Candidate Discovery Challenge. The sandbox provides a visual dashboard to evaluate, calibrate, and monitor candidate suitability against complex job descriptions (JDs) in a CPU-optimized, zero-latency, and privacy-preserving environment.

---

## Architecture Overview

The scoring engine processes candidate pools using a multi-phase pipeline that filters, tokenizes, embeds, and scores profiles against target job specifications, automatically synchronizing results to collaborative channels upon completion:

```
  [106K Candidate Profiles (JSONL)]
                 │
                 ▼
  ┌─────────────────────────────┐
  │   Phase 1: Ingest & Parse   │  ◄── Schema validation & title normalization
  └──────────────┬──────────────┘
                 │ (106K candidates)
                 ▼
  ┌─────────────────────────────┐
  │ Phase 2: Hybrid Sparse      │  ◄── BM25 filtering using JD Core Skills
  │          Pre-Retrieval      │      (Recalls top 8,000 tech-aligned profiles)
  └──────────────┬──────────────┘
                 │ (Top 8,000 candidates)
                 ▼
  ┌─────────────────────────────┐
  │ Phase 3: Dense Embeddings   │  ◄── CPU Batch encoding using Sentence Transformers
  │          & 5-Signal Fusion  │      (all-MiniLM-L6-v2) across 5 independent vectors
  └──────────────┬──────────────┘
                 │ (Scored candidate pool)
                 ▼
  ┌─────────────────────────────┐
  │ Phase 4: Post-Filters &     │  ◄── Notice period penalties, Open-To-Work multipliers,
  │          Agentic Re-Ranking │      and alphabetical tie-breakers
  └──────────────┬──────────────┘
                 │
                 ▼
           [Top 100 Shortlist]
                 │
                 ├──► Generate submission.csv
                 ├──► Auto-fire Slack notification (Top 5 Block Kit payload)
                 └──► Auto-sync to Google Sheets (gspread authorizer)
```

---

## Core Features & Recruiter Capabilities

The platform includes several core workflows engineered to streamline candidate evaluation and collaborative decision-making:

### 1. Interactive Candidate Ranker
*   **Dual-Tab Detail View:** Recruiters can toggle between **Evaluation & Insights** (Plotly radar charts, score breakdowns, and AI rationales) and the **Original Resume** view.
*   **A4 Resume PDF Viewer:** Renders a browser-style PDF reader canvas. It features a grey toolbar with document titles (`Resume_[Name].pdf`), mock page counts, zoom controls, print/download icons, and a white, highly styled A4-formatted page displaying the candidate's actual profile, summary, experience timeline, education, and skills.
*   **Quick-Action Buttons:** Recruiters can **Shortlist (✓)** or **Reject (✗)** candidates directly from their detail panel. 
*   **Dynamic Sidebar Styling:** Sidebar candidate cards update instantly. Shortlisted candidates receive a green left-border and a checkmark (`✓`), while rejected candidates fade out (`opacity: 0.55`) and receive a cross (`✗`).

### 2. Recruiter Memory & Active Calibration
*   **Memory Feed:** Tracks learned hiring preferences and weight adjustments (e.g., skill assessment thresholds, notice period penalties).
*   **Real-time Decision Counter:** Captures manual shortlist and reject clicks, incrementing the total candidate decisions metric in real time.
*   **Active Confidence Engine:** Dynamically increases the **Memory Confidence** calibration rating by `+2%` for each manual action (up to a `+10%` boost), demonstrating active learning from recruiter feedback.
*   **Bias Transparency Report:** Interactive Plotly bar chart displaying the magnitude of score adjustments to ensure override transparency.

### 3. Analytics Dashboard
*   **Score Distribution Histogram:** Displays score spreads of the overall candidate pool vs. the top 100 shortlisted candidates, confirming clear scoring separation.
*   **Radial Cluster Web:** Plotly Scatterpolar chart showing candidate alignment across the five scoring dimensions.
*   **Availability Pool:** Visualizes candidate readiness (active, passive, notice period spreads).

### 4. Integrations Hub
*   **Slack Webhook Integration:** Formats and delivers the top 5 candidates as a styled Slack Block Kit payload immediately upon ranking completion.
*   **Google Sheets Exporter:** Dynamically writes candidate scores, metadata, and AI rationales to a configured spreadsheet using `gspread`. Includes an **Open Last Export** button linking directly to the live sheet, and a **Re-export** button to trigger manual syncs.
*   **Twilio WhatsApp API:** Supports simulated SMS/WhatsApp routing using active Twilio REST API credentials.

---

## Mathematical Breakdown of the 5 Scoring Signals

Candidates are scored on a scale of `0.0` to `1.0` across five independent dimensions, which are then combined using weights calibrated from historical recruitment runs:

### 1. Semantic Fit (30% Weight)
Calculates the cosine similarity between the candidate text representation (summary, headline, current title, skills, and work history descriptions) and the precomputed job description embedding:
$$\text{Semantic Score} = \frac{\mathbf{E}_{\text{candidate}} \cdot \mathbf{E}_{\text{JD}}}{\|\mathbf{E}_{\text{candidate}}\| \|\mathbf{E}_{\text{JD}}\|}$$
*   **Encoder**: `all-MiniLM-L6-v2` (running locally on CPU).

### 2. Core Skills Match (25% Weight)
Evaluates the candidate's skills list against the JD core skills, factoring in proficiency levels and skill adjacency mappings:
*   **Proficiency Weights**: Beginner (`0.4`), Intermediate (`0.6`), Advanced (`0.85`), Expert (`1.0`).
*   **Verified Override**: Candidates who completed a verified Redrob assessment in a core skill with a score $\ge 75$ are auto-overridden to Expert (`1.0`).
*   **Adjacency Scoring**: If a core skill is missing, the engine checks for adjacent skill mappings (e.g., Python $\rightarrow$ R, PyTorch $\rightarrow$ TensorFlow) and awards a partial score (`0.40`).

### 3. Career Trajectory (20% Weight)
Evaluates career growth, background stability, and education alignment:
*   **Seniority Map**: Job titles are mapped to seniority weights (CTO: `1.0`, Intern: `0.1`).
*   **Company Progression**: Awards a bonus for growth in company size or scope across past positions.
*   **Education Tier**: Awards a tier-based bonus (Tier-1: `+0.15`, Tier-2: `+0.10`) for academic pedigree.
*   **Service Consulting Penalty**: Applies a `0.85x` multiplier if the candidate's active employment is at a service consulting firm (e.g., TCS, Wipro, Infosys).

### 4. Behavioral Engagement (15% Weight)
A composite score reflecting candidate availability, responsiveness, and completeness:
*   **Completeness (18%)**: Ratio of filled profile fields.
*   **Freshness (12%)**: Activity decay based on `last_active_date` up to 90 days.
*   **Responsiveness (25%)**: Aggregated response rates and interview completion metrics.
*   **GitHub Activity (15%)**: Open-source contributions.
*   **Acceptance Rate (10%)**: Historical offer acceptance rates.
*   **Notice Period (10%)**: Scaled notice period score: $\max(0.0, 1.0 - \frac{\text{notice\_period\_days}}{180})$.
*   **Open to Work (5%)** and **Verification Status (5%)**.
*   **Relocation Bonus**: Adds a flat `+0.05` bonus if the candidate is willing to relocate or open to remote work.

### 5. Domain Alignment (10% Weight)
Matches candidate industry backgrounds against target sectors (e.g., AI, SaaS, FinTech, HR-tech) using keyword frequency counts in past experience roles.

---

## Post-Scoring Adjustments & Tie-Breakers

-   **Availability Multiplier**: A post-fusion multiplier of `0.75x` is applied if `open_to_work_flag` is `False`.
-   **Tie-Breaker**: If final scores are identical, ties are broken using `candidate_id` in lexicographical ascending order to guarantee deterministic ranking.
-   **Memory Constraints**:
    -   *Notice Period Penalty*: If memory calibration is active and a candidate's notice period exceeds 90 days, a penalty of `-0.08` is deducted from their score.
    -   *Response Rate Filter*: If memory calibration is active, candidates with a recruiter response rate $< 55\%$ are filtered out.

---

## Codebase Directory Structure

```
├── .streamlit/
│   └── config.toml           # Streamlit server configuration
├── analytics/
│   ├── charts.py             # Plotly chart builders (Radar, Histogram, Bar)
│   ├── data_store.py         # Recruiter memory database I/O and run history seeding
│   └── metrics.py            # Signal correlation calculations
├── assets/                   # Static icons, SVGs, and images
├── data/                     # Offline database storage
├── integrations/
│   ├── api.py                # Background FastAPI server
│   ├── activity_log.py       # Logger for integration events
│   ├── csv_export.py         # Formatted CSV exporter
│   ├── sheets.py             # Google Sheets API writing engine
│   └── slack.py              # Slack API notification trigger
├── pages/
│   ├── analytics_page.py     # Analytics Tab layout and rendering logic
│   └── recruiter_memory_page.py # Recruiter Memory Tab layout and rendering logic
├── app.py                    # Main dashboard entrypoint and Candidate Ranker layout
├── integrations_ui.py        # Integrations Tab layout and active API log console
├── slack_notifier.py         # Slack Block Kit message builder & sender
├── rank.py                   # Core mathematical scoring and filtering pipeline
├── precompute.py             # JD skill extraction script
└── validate_submission.py    # Submission formatting validator
```

---

## Secrets & Configuration

To enable the active integrations, configure the following secrets inside your `.streamlit/secrets.toml` file (for local runs) or Hugging Face Space secrets (for remote deployment):

```toml
# Slack Integration
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/..."

# Google Sheets Integration
GOOGLE_SHEETS_ID = "18M-F627QY7WI4tY7..."
GOOGLE_SERVICE_ACCOUNT = '{"type": "service_account", "project_id": "...", ...}'

# WhatsApp/SMS Integration
TWILIO_SID = "AC..."
TWILIO_AUTH = "..."
TWILIO_PHONE = "+1..."

# API Authorization
CALIPR_API_KEY = "calipr_live_..."
```

---

## Local Setup & CLI Execution

### 1. Installation
Ensure you have Python 3.10+ installed. Clone the repository and install the dependencies:
```bash
pip install -r requirements.txt
```

### 2. Running the App
Start the Streamlit dashboard:
```bash
streamlit run app.py
```
The app will automatically launch a background API server on port `7861` to power the Integrations tab.

### 3. Running the Pipeline via CLI
If you wish to execute the pipeline directly via terminal commands:
```bash
# Step 1: Pre-compute job description embeddings
python precompute.py

# Step 2: Rank candidates from a dataset file
python rank.py --candidates data/candidates.jsonl --out outputs/submission.csv

# Step 3: Validate the output formatting
python validate_submission.py outputs/submission.csv
```

---

## Deployment to Hugging Face Spaces

This repository is configured for direct deployment to Hugging Face Spaces using the Streamlit SDK.

To deploy manually:
1.  Initialize git and add the Hugging Face space remote:
    ```bash
    git init
    git remote add origin https://huggingface.co/spaces/Aumus/calipr
    ```
2.  Commit and push the branch:
    ```bash
    git add .
    git commit -m "Deploy sandbox application"
    git push origin main --force
    ```
Hugging Face will automatically detect `app.py` as the entrypoint (specified in the metadata) and build the space.
