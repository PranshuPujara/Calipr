import React, { useState, useEffect } from 'react';
import { Play, Sparkles, Check, Server, Search, BarChart2, Award } from 'lucide-react';

const RunPipeline = ({ backendUrl, onRunSuccess }) => {
  const [jdText, setJdText] = useState(`Job Title: Senior Backend Engineer
Required Experience: 5+ years
Domain: Cloud Systems, Scalable Databases
Core Requirements:
- Heavy production experience with Python, FastAPI, and Docker.
- Advanced SQL optimization, particularly PostgreSQL indexing.
- Familiarity with vector embeddings, FAISS, or hybrid search systems is a huge plus.
- Proven track record of leading API design and mentoring junior developers.`);
  const [minYears, setMinYears] = useState(5);
  const [provider, setProvider] = useState('groq');
  
  // Pipeline status states
  const [isRunning, setIsRunning] = useState(false);
  const [runError, setRunError] = useState('');
  const [activeStep, setActiveStep] = useState(0);

  const pipelineSteps = [
    { label: "Phase 1: Job Description Parsing & Experience Filtering", icon: Server },
    { label: "Phase 2: Hybrid Dense-Sparse Retrieval (FAISS + BM25)", icon: Search },
    { label: "Phase 3: 5-Signal Mathematical Evaluation (Weighted Fusion)", icon: BarChart2 },
    { label: "Phase 4: Agentic Re-Ranking (Groq/Gemini Rationale Logic)", icon: Award }
  ];

  useEffect(() => {
    let interval;
    if (isRunning) {
      setActiveStep(0);
      interval = setInterval(() => {
        setActiveStep(prev => {
          if (prev < pipelineSteps.length - 1) {
            return prev + 1;
          }
          return prev;
        });
      }, 1800); // Progress to next simulated stage every 1.8s
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [isRunning]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!jdText.trim()) {
      setRunError('Please enter a job description to evaluate.');
      return;
    }

    setIsRunning(true);
    setRunError('');

    try {
      const res = await fetch(`${backendUrl}/api/pipeline/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jd_text: jdText,
          min_years: parseInt(minYears) || 0,
          provider: provider
        }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Evaluation run failed.');
      }

      const runRecord = await res.json();
      
      // Delay success slightly to ensure user sees Phase 4 done state
      setTimeout(() => {
        setIsRunning(false);
        onRunSuccess(runRecord);
      }, 1000);
      
    } catch (err) {
      setRunError(err.message || 'Failed to complete candidate ranking.');
      setIsRunning(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <div className="page-title">
          <h1>Run Recruitment Pipeline</h1>
          <p>Execute retrieval, 5-signal scoring, and LLM re-ranking on your candidate pool.</p>
        </div>
      </div>

      <div className="split-pane" style={{ gridTemplateColumns: isRunning ? '1fr' : '1.2fr 0.8fr' }}>
        {/* Input Form Column */}
        {!isRunning ? (
          <>
            <div className="glass-container" style={{ margin: 0 }}>
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label htmlFor="jd-text">Paste Job Description</label>
                  <textarea 
                    id="jd-text"
                    required
                    rows="14"
                    value={jdText}
                    onChange={(e) => setJdText(e.target.value)}
                    placeholder="Enter the job title, requirements, key technical skills, and experience details..."
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                  <div className="form-group">
                    <label htmlFor="min-years">Min Experience Override (Years)</label>
                    <input 
                      type="number" 
                      id="min-years" 
                      min="0"
                      max="25"
                      value={minYears}
                      onChange={(e) => setMinYears(e.target.value)}
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="provider">LLM Re-ranking Provider</label>
                    <select 
                      id="provider"
                      value={provider}
                      onChange={(e) => setProvider(e.target.value)}
                    >
                      <option value="groq">Groq (Llama-3-70b-ToolUse)</option>
                      <option value="gemini">Gemini (Pro-1.5-Engine)</option>
                    </select>
                  </div>
                </div>

                {runError && (
                  <div style={{ color: 'var(--accent-coral)', fontSize: '13px', margin: '16px 0' }}>
                    {runError}
                  </div>
                )}

                <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '14px', marginTop: '12px' }}>
                  <Sparkles size={16} className="nav-icon" />
                  Evaluate & Rank Candidate Pool
                </button>
              </form>
            </div>

            {/* Sidebar Guidance info */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div className="dashboard-card" style={{ background: 'rgba(132, 185, 239, 0.05)', border: '1px dashed var(--primary-lighter)' }}>
                <h4 style={{ color: 'var(--primary-dark)', marginBottom: '8px' }}>Pipeline Execution Info</h4>
                <p style={{ fontSize: '13px', color: 'var(--text-body)', lineHeight: 1.6 }}>
                  Calipr uses a multi-tiered pipeline that executes <strong>dense-vector search</strong> (using FAISS) and <strong>sparse keyword matching</strong> (using BM25) first.
                </p>
                <p style={{ fontSize: '13px', color: 'var(--text-body)', lineHeight: 1.6, marginTop: '8px' }}>
                  Only the top 20 candidates retrieved by the search filters are fed into the LLM re-ranker, saving massive token costs while ensuring explainable outcomes.
                </p>
              </div>

              <div className="dashboard-card">
                <h4 style={{ marginBottom: '8px' }}>Active Weights</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '13px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Semantic Fit:</span>
                    <strong style={{ fontFamily: 'var(--font-mono)' }}>30%</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Technical Skills Match:</span>
                    <strong style={{ fontFamily: 'var(--font-mono)' }}>25%</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Career Trajectory:</span>
                    <strong style={{ fontFamily: 'var(--font-mono)' }}>20%</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Behavioral Signals:</span>
                    <strong style={{ fontFamily: 'var(--font-mono)' }}>15%</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Domain Alignment:</span>
                    <strong style={{ fontFamily: 'var(--font-mono)' }}>10%</strong>
                  </div>
                </div>
              </div>
            </div>
          </>
        ) : (
          /* Running Pipeline Loading Screen */
          <div className="glass-container loader-wrapper" style={{ minHeight: '400px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <div className="pulse-spinner" />
            <h3 style={{ marginTop: '12px' }}>Executing Calipr Ranking Engine</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '14px', marginBottom: '24px' }}>
              Processing candidate vectors and computing multi-dimensional signal weights...
            </p>

            <div className="pipeline-progress-list">
              {pipelineSteps.map((step, idx) => {
                const Icon = step.icon;
                let stepClass = "pipeline-progress-step";
                if (idx < activeStep) stepClass += " done";
                else if (idx === activeStep) stepClass += " active";
                
                return (
                  <div key={idx} className={stepClass}>
                    <div className="progress-dot" />
                    <Icon size={16} />
                    <span>{step.label}</span>
                    {idx < activeStep && <Check size={14} style={{ marginLeft: 'auto', color: 'var(--accent-green)' }} />}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RunPipeline;
