import React, { useState } from 'react';
import { Upload, Plus, Search, FileText, UserPlus, Eye, X, Check, Loader2 } from 'lucide-react';

const CandidatesPool = ({ candidates, onRefresh, backendUrl }) => {
  const [search, setSearch] = useState('');
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showManualModal, setShowManualModal] = useState(false);
  
  // Upload states
  const [uploadFile, setUploadFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [uploadSuccess, setUploadSuccess] = useState(false);
  
  // Manual form states
  const [manualJson, setManualJson] = useState(JSON.stringify({
    "name": "Jane Doe",
    "email": "jane.doe@example.com",
    "current_title": "Senior React Engineer",
    "years_experience": 5,
    "skills": ["React", "TypeScript", "JavaScript", "HTML", "CSS", "Webpack"],
    "domains": ["Frontend", "E-commerce"],
    "behavioral_signals": {
      "profile_completeness": 0.9,
      "response_speed_hours": 8.0,
      "portfolio_depth": 0.8
    },
    "career_progression": [
      {
        "title": "Senior Frontend Developer",
        "company": "ShopTech",
        "duration_months": 24
      },
      {
        "title": "Frontend Developer",
        "company": "Web Agency",
        "duration_months": 36
      }
    ]
  }, null, 2));
  const [manualError, setManualError] = useState('');
  const [manualSuccess, setManualSuccess] = useState(false);

  // Filter candidates
  const filteredCandidates = candidates.filter(c => {
    const term = search.toLowerCase();
    const name = (c.name || '').toLowerCase();
    const title = (c.current_title || '').toLowerCase();
    const skills = (c.skills || []).map(s => s.toLowerCase()).join(' ');
    return name.includes(term) || title.includes(term) || skills.includes(term);
  });

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setUploadFile(e.target.files[0]);
      setUploadError('');
      setUploadSuccess(false);
    }
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!uploadFile) {
      setUploadError('Please select a file to upload.');
      return;
    }

    setIsUploading(true);
    setUploadError('');
    
    const formData = new FormData();
    formData.append('file', uploadFile);
    formData.append('provider', 'groq'); // Use default groq parser

    try {
      const res = await fetch(`${backendUrl}/api/candidates/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Resume upload failed.');
      }

      const data = await res.json();
      setUploadSuccess(true);
      setUploadFile(null);
      onRefresh(); // Refresh parent candidate pool state
      setTimeout(() => setShowUploadModal(false), 1500);
    } catch (err) {
      setUploadError(err.message || 'Error parsing resume.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleManualSubmit = async (e) => {
    e.preventDefault();
    setManualError('');
    setManualSuccess(false);

    try {
      const parsedData = jsonValidate(manualJson);
      
      const res = await fetch(`${backendUrl}/api/candidates/manual`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(parsedData),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Failed to save candidate profile.');
      }

      setManualSuccess(true);
      onRefresh();
      setTimeout(() => setShowManualModal(false), 1500);
    } catch (err) {
      setManualError(err.message || 'Invalid JSON format.');
    }
  };

  const jsonValidate = (str) => {
    try {
      return JSON.parse(str);
    } catch (e) {
      throw new Error("Invalid JSON: Please check your syntax, brackets, and quotes.");
    }
  };

  return (
    <div>
      <div className="page-header">
        <div className="page-title">
          <h1>Candidates Pool ({candidates.length})</h1>
          <p>Register, parse, and browse your database of candidate profiles.</p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn btn-secondary" onClick={() => { setShowUploadModal(true); setUploadError(''); setUploadSuccess(false); }}>
            <Upload size={16} />
            Upload Resume (PDF/TXT)
          </button>
          <button className="btn btn-primary" onClick={() => { setShowManualModal(true); setManualError(''); setManualSuccess(false); }}>
            <UserPlus size={16} />
            Add Profile JSON
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="glass-container" style={{ padding: '20px', marginBottom: '24px', display: 'flex', gap: '16px', alignItems: 'center' }}>
        <div style={{ position: 'relative', flexGrow: 1 }}>
          <Search size={18} style={{ position: 'absolute', left: '16px', top: '12px', color: 'var(--text-muted)' }} />
          <input 
            type="text" 
            placeholder="Search candidates by name, job title, or specific technical skills..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ paddingLeft: '44px' }}
          />
        </div>
      </div>

      {/* Candidate Pool Table */}
      <div className="candidate-table-wrapper">
        <table className="candidate-table">
          <thead>
            <tr>
              <th>Candidate</th>
              <th>Current Title</th>
              <th>Experience</th>
              <th>Core Tech Stack</th>
              <th>Signal Profile</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredCandidates.length === 0 ? (
              <tr>
                <td colSpan="6" style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)' }}>
                  No candidates found matching the search criteria.
                </td>
              </tr>
            ) : (
              filteredCandidates.map((c) => (
                <tr key={c.candidate_id}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <div className="avatar-circle">
                        {(c.name || 'C').split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()}
                      </div>
                      <div>
                        <div style={{ fontWeight: 600, color: 'var(--text-dark)' }}>{c.name}</div>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{c.email}</div>
                      </div>
                    </div>
                  </td>
                  <td>{c.current_title}</td>
                  <td>
                    <span className="badge badge-blue">
                      {c.years_experience} Years
                    </span>
                  </td>
                  <td>
                    <div className="skill-tag-list" style={{ maxWidth: '360px' }}>
                      {(c.skills || []).slice(0, 5).map((skill, idx) => (
                        <span key={idx} className="skill-tag">{skill}</span>
                      ))}
                      {(c.skills || []).length > 5 && (
                        <span className="skill-tag" style={{ background: 'transparent', borderStyle: 'dashed' }}>
                          +{(c.skills || []).length - 5} more
                        </span>
                      )}
                    </div>
                  </td>
                  <td>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '12px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', width: '130px' }}>
                        <span>Completeness:</span>
                        <span style={{ fontWeight: 600 }}>{((c.behavioral_signals?.profile_completeness || 0) * 100).toFixed(0)}%</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', width: '130px' }}>
                        <span>Response Speed:</span>
                        <span style={{ fontWeight: 600 }}>{c.behavioral_signals?.response_speed_hours || 24}h</span>
                      </div>
                    </div>
                  </td>
                  <td>
                    <button 
                      className="btn btn-secondary btn-sm"
                      style={{ padding: '6px 12px', display: 'flex', alignItems: 'center', gap: '4px' }}
                      onClick={() => setSelectedCandidate(c)}
                    >
                      <Eye size={14} />
                      View Profile
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Candidate Details Drawer Modal */}
      {selectedCandidate && (
        <div style={{ position: 'fixed', top: 0, right: 0, bottom: 0, left: 0, background: 'rgba(26,22,21,0.3)', backdropFilter: 'blur(4px)', zIndex: 1000, display: 'flex', justifyContent: 'flex-end' }}>
          <div style={{ width: '100%', maxWidth: '640px', background: 'var(--bg-pure-white)', boxShadow: 'var(--shadow-xl)', display: 'flex', flexDirection: 'column', padding: '40px', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px', borderBottom: '1px solid var(--border)', paddingBottom: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <div className="avatar-circle" style={{ width: '60px', height: '60px', fontSize: '22px' }}>
                  {selectedCandidate.name.split(' ').map(n => n[0]).join('').substring(0,2).toUpperCase()}
                </div>
                <div>
                  <h2 style={{ fontSize: '24px' }}>{selectedCandidate.name}</h2>
                  <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>{selectedCandidate.email} · {selectedCandidate.current_title}</p>
                </div>
              </div>
              <button 
                onClick={() => setSelectedCandidate(null)}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}
              >
                <X size={24} />
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <div>
                <h4 style={{ marginBottom: '10px', fontSize: '14px', textTransform: 'uppercase', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>Experience Summary</h4>
                <p><strong>Total Experience:</strong> {selectedCandidate.years_experience} Years</p>
                <p><strong>Domains:</strong> {selectedCandidate.domains?.join(', ') || 'N/A'}</p>
              </div>

              <div>
                <h4 style={{ marginBottom: '10px', fontSize: '14px', textTransform: 'uppercase', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>Technical Skills</h4>
                <div className="skill-tag-list">
                  {selectedCandidate.skills?.map((skill, idx) => (
                    <span key={idx} className="skill-tag">{skill}</span>
                  ))}
                </div>
              </div>

              <div>
                <h4 style={{ marginBottom: '10px', fontSize: '14px', textTransform: 'uppercase', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>Career Progression</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {selectedCandidate.career_progression?.map((job, idx) => (
                    <div key={idx} style={{ background: '#fafafa', border: '1px solid var(--border)', padding: '12px', borderRadius: 'var(--radius-sm)' }}>
                      <div style={{ fontWeight: 600, color: 'var(--text-dark)' }}>{job.title}</div>
                      <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>{job.company} · {job.duration_months} months</div>
                    </div>
                  )) || <p style={{ color: 'var(--text-muted)' }}>No historical jobs logged.</p>}
                </div>
              </div>

              {selectedCandidate.resume_text && (
                <div>
                  <h4 style={{ marginBottom: '10px', fontSize: '14px', textTransform: 'uppercase', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>Extracted Resume Text</h4>
                  <div style={{ background: '#fafafa', border: '1px solid var(--border)', padding: '16px', borderRadius: 'var(--radius-sm)', maxHeight: '200px', overflowY: 'auto', fontSize: '12px', fontFamily: 'var(--font-mono)', whiteSpace: 'pre-line', color: 'var(--text-body)' }}>
                    {selectedCandidate.resume_text}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Upload Resume Modal */}
      {showUploadModal && (
        <div style={{ position: 'fixed', top: 0, right: 0, bottom: 0, left: 0, background: 'rgba(26,22,21,0.4)', backdropFilter: 'blur(4px)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div className="glass-container" style={{ width: '100%', maxWidth: '480px', margin: 0, padding: '32px', background: 'var(--bg-pure-white)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
              <h3>Parse Resume File</h3>
              <button onClick={() => setShowUploadModal(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}><X size={20} /></button>
            </div>

            <form onSubmit={handleUploadSubmit}>
              <div style={{ border: '2px dashed var(--border)', padding: '40px 20px', borderRadius: 'var(--radius-md)', textAlign: 'center', marginBottom: '20px', cursor: 'pointer', background: '#fafafa' }}>
                <input 
                  type="file" 
                  accept=".pdf,.txt" 
                  id="resume-file" 
                  onChange={handleFileChange} 
                  style={{ display: 'none' }} 
                />
                <label htmlFor="resume-file" style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
                  <FileText size={40} style={{ color: 'var(--text-muted)' }} />
                  <div>
                    <span style={{ fontWeight: 600, color: 'var(--primary-dark)' }}>Click to upload</span> or drag and drop
                  </div>
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>PDF or TXT resumes (Max 10MB)</span>
                </label>
              </div>

              {uploadFile && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'var(--primary-light)', padding: '8px 16px', borderRadius: 'var(--radius-sm)', marginBottom: '20px', fontSize: '13px' }}>
                  <Check size={16} style={{ color: 'var(--primary-dark)' }} />
                  <span style={{ flexGrow: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{uploadFile.name}</span>
                </div>
              )}

              {uploadError && (
                <div style={{ color: 'var(--accent-coral)', fontSize: '13px', marginBottom: '20px' }}>
                  {uploadError}
                </div>
              )}

              {uploadSuccess && (
                <div style={{ color: 'var(--accent-green)', fontSize: '13px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Check size={16} /> Candidate parsed and saved persistently!
                </div>
              )}

              <button 
                type="submit" 
                className="btn btn-primary" 
                style={{ width: '100%' }}
                disabled={isUploading}
              >
                {isUploading ? (
                  <>
                    <Loader2 size={16} className="nav-icon" style={{ animation: 'spin 1s linear infinite' }} />
                    Parsing Resume with LLM...
                  </>
                ) : "Parse & Append Candidate"}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Manual JSON Modal */}
      {showManualModal && (
        <div style={{ position: 'fixed', top: 0, right: 0, bottom: 0, left: 0, background: 'rgba(26,22,21,0.4)', backdropFilter: 'blur(4px)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div className="glass-container" style={{ width: '100%', maxWidth: '580px', margin: 0, padding: '32px', background: 'var(--bg-pure-white)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
              <h3>Add Candidate JSON Profile</h3>
              <button onClick={() => setShowManualModal(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}><X size={20} /></button>
            </div>

            <form onSubmit={handleManualSubmit}>
              <div className="form-group" style={{ marginBottom: '16px' }}>
                <label>Profile JSON Content</label>
                <textarea 
                  value={manualJson}
                  onChange={(e) => setManualJson(e.target.value)}
                  rows="12"
                  style={{ fontFamily: 'var(--font-mono)', fontSize: '12px' }}
                />
              </div>

              {manualError && (
                <div style={{ color: 'var(--accent-coral)', fontSize: '13px', marginBottom: '16px' }}>
                  {manualError}
                </div>
              )}

              {manualSuccess && (
                <div style={{ color: 'var(--accent-green)', fontSize: '13px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Check size={16} /> Candidate added successfully!
                </div>
              )}

              <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>
                Submit Candidate Profile
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default CandidatesPool;
