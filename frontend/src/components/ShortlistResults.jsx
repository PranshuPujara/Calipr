import React, { useState, useEffect } from 'react';
import RadarChart from './RadarChart';
import { Award, Briefcase, Mail, Star, FileText, ChevronRight, HelpCircle } from 'lucide-react';

const ShortlistResults = ({ activeRun, setView }) => {
  const [selectedCandidateId, setSelectedCandidateId] = useState('');
  
  const shortlist = activeRun?.shortlist || [];
  
  useEffect(() => {
    if (shortlist.length > 0) {
      setSelectedCandidateId(shortlist[0].candidate_id);
    }
  }, [activeRun, shortlist]);

  if (!activeRun) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 0' }}>
        <h2 style={{ marginBottom: '16px' }}>No Shortlist Loaded</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '24px' }}>Please go to the dashboard to select a past run or launch a new evaluation.</p>
        <button className="btn btn-primary" onClick={() => setView('dashboard')}>
          Go to Dashboard
        </button>
      </div>
    );
  }

  const selectedCandidate = shortlist.find(c => c.candidate_id === selectedCandidateId);

  return (
    <div>
      <div className="page-header">
        <div className="page-title">
          <h1>Evaluation Shortlist</h1>
          <p>
            Ranked candidate matches for <strong>{activeRun.jd_summary?.title || "AI Recruiter Run"}</strong>
          </p>
        </div>
        <div style={{ fontSize: '12px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
          Run ID: {activeRun.run_id.substring(0, 8)}... · {shortlist.length} Matches Ranked
        </div>
      </div>

      <div className="split-pane">
        {/* Left Pane: Candidate Rankings List */}
        <div className="pane-left">
          {shortlist.length === 0 ? (
            <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '20px' }}>
              No candidates matched the experience filters for this run.
            </div>
          ) : (
            shortlist.map((c, idx) => (
              <div 
                key={c.candidate_id} 
                className={`shortlist-item ${selectedCandidateId === c.candidate_id ? 'active' : ''}`}
                onClick={() => setSelectedCandidateId(c.candidate_id)}
              >
                <div className="shortlist-rank">#{idx + 1}</div>
                <div className="shortlist-details">
                  <div className="shortlist-name">{c.name}</div>
                  <div className="shortlist-title">{c.current_title}</div>
                </div>
                <div className="shortlist-score">
                  {(c.composite_score * 100).toFixed(1)}%
                </div>
              </div>
            ))
          )}
        </div>

        {/* Right Pane: Selected Candidate Explainable Details */}
        <div className="pane-right">
          {selectedCandidate ? (
            <>
              {/* Header Info */}
              <div className="glass-container" style={{ margin: 0, padding: '24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <div className="avatar-circle" style={{ width: '52px', height: '52px', fontSize: '18px' }}>
                      {selectedCandidate.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()}
                    </div>
                    <div>
                      <h2 style={{ fontSize: '20px' }}>{selectedCandidate.name}</h2>
                      <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>{selectedCandidate.current_title}</p>
                    </div>
                  </div>
                  
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                      Composite Score
                    </div>
                    <div style={{ fontSize: '28px', fontWeight: 600, color: 'var(--text-dark)' }}>
                      {(selectedCandidate.composite_score * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '16px', marginTop: '20px', fontSize: '13px', borderTop: '1px solid var(--border)', paddingTop: '16px', color: 'var(--text-body)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Mail size={14} className="nav-icon" />
                    {selectedCandidate.email}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Briefcase size={14} className="nav-icon" />
                    {selectedCandidate.years_experience} Years Experience
                  </div>
                </div>
              </div>

              {/* Rationale & Explainable AI */}
              <div className="glass-container" style={{ margin: 0, padding: '24px' }}>
                <h4 style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Award size={18} style={{ color: 'var(--accent-amber)' }} />
                  Evaluation Rationale
                </h4>
                <p style={{ fontSize: '14px', lineHeight: '1.6', color: 'var(--text-body)', whiteSpace: 'pre-line' }}>
                  {selectedCandidate.rationale}
                </p>
              </div>

              {/* Radar Chart & Score Breakdowns */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px' }}>
                <div className="glass-container" style={{ margin: 0, padding: '20px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                  <h4 style={{ alignSelf: 'flex-start', marginBottom: '16px' }}>5-Signal Radar Map</h4>
                  <RadarChart scores={selectedCandidate.signal_breakdown} width={280} height={280} />
                </div>

                {/* Score breakdown listing */}
                <div className="glass-container" style={{ margin: 0, padding: '24px' }}>
                  <h4 style={{ marginBottom: '16px' }}>Axes Breakdown</h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                    {Object.entries(selectedCandidate.signal_breakdown || {}).map(([key, val]) => {
                      // Map key back to labels
                      const labelMap = {
                        semantic: { name: "Semantic Fit", color: "var(--primary)" },
                        skills: { name: "Skills Match", color: "var(--accent-green)" },
                        trajectory: { name: "Career Trajectory", color: "var(--accent-amber)" },
                        behavioral: { name: "Behavioral Signals", color: "var(--accent-coral)" },
                        domain: { name: "Domain Alignment", color: "var(--accent-brown)" }
                      };
                      const item = labelMap[key] || { name: key, color: 'var(--text-dark)' };
                      
                      return (
                        <div key={key} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                            <span style={{ fontWeight: 500 }}>{item.name}</span>
                            <span style={{ fontWeight: 600, fontFamily: 'var(--font-mono)' }}>{(val * 100).toFixed(0)}%</span>
                          </div>
                          <div style={{ height: '6px', background: 'var(--bg-cream)', borderRadius: '999px', overflow: 'hidden' }}>
                            <div style={{ height: '100%', background: item.color, width: `${val * 100}%`, borderRadius: '999px' }} />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* Skills Tags */}
              <div className="glass-container" style={{ margin: 0, padding: '24px' }}>
                <h4 style={{ marginBottom: '12px' }}>Technical Skill Tags</h4>
                <div className="skill-tag-list">
                  {selectedCandidate.skills?.map((skill, idx) => (
                    <span key={idx} className="skill-tag">{skill}</span>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)' }}>
              Select a candidate from the shortlist to view details.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ShortlistResults;
