import React, { useState, useEffect } from 'react';
import { LayoutDashboard, Users, Play, ListOrdered, Settings as SettingsIcon, ShieldAlert, RefreshCw } from 'lucide-react';
import Dashboard from './components/Dashboard';
import CandidatesPool from './components/CandidatesPool';
import RunPipeline from './components/RunPipeline';
import ShortlistResults from './components/ShortlistResults';
import Settings from './components/Settings';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

function App() {
  const [view, setView] = useState('dashboard');
  const [candidates, setCandidates] = useState([]);
  const [history, setHistory] = useState([]);
  const [activeRun, setActiveRun] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Fetch initial candidates and history
  const fetchData = async () => {
    setIsLoading(true);
    setError('');
    try {
      const candRes = await fetch(`${BACKEND_URL}/api/candidates`);
      const histRes = await fetch(`${BACKEND_URL}/api/history`);

      if (!candRes.ok || !histRes.ok) {
        throw new Error("Failed to load pipeline data from backend server.");
      }

      const candData = await candRes.json();
      const histData = await histRes.json();

      setCandidates(candData);
      setHistory(histData);
    } catch (err) {
      console.error(err);
      setError("Server connection failed. Make sure the FastAPI backend is running on port 8000.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSelectRun = (run) => {
    setActiveRun(run);
    setView('shortlist');
  };

  const handleRunSuccess = (newRun) => {
    setActiveRun(newRun);
    setHistory(prev => [newRun, ...prev]);
    setView('shortlist');
  };

  const renderActiveView = () => {
    switch(view) {
      case 'dashboard':
        return (
          <Dashboard 
            candidates={candidates} 
            history={history} 
            onSelectRun={handleSelectRun} 
            setView={setView} 
          />
        );
      case 'candidates':
        return (
          <CandidatesPool 
            candidates={candidates} 
            onRefresh={fetchData} 
            backendUrl={BACKEND_URL} 
          />
        );
      case 'run-pipeline':
        return (
          <RunPipeline 
            backendUrl={BACKEND_URL} 
            onRunSuccess={handleRunSuccess} 
          />
        );
      case 'shortlist':
        return (
          <ShortlistResults 
            activeRun={activeRun} 
            setView={setView} 
          />
        );
      case 'settings':
        return (
          <Settings 
            backendUrl={BACKEND_URL} 
          />
        );
      default:
        return <Dashboard candidates={candidates} history={history} setView={setView} />;
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="brand-section">
          <svg className="brand-logo-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 2V22" stroke="currentColor" stroke-width="3.2" stroke-linecap="square"/>
            <path d="M4 14H19" stroke="currentColor" stroke-width="3.2" stroke-linecap="square"/>
            <path d="M13.5 9V22" stroke="currentColor" stroke-width="3.2" stroke-linecap="square"/>
          </svg>
          <span>Calipr App</span>
        </div>

        <nav className="nav-menu">
          <div 
            className={`nav-item ${view === 'dashboard' ? 'active' : ''}`}
            onClick={() => setView('dashboard')}
          >
            <LayoutDashboard className="nav-icon" />
            <span>Dashboard</span>
          </div>

          <div 
            className={`nav-item ${view === 'candidates' ? 'active' : ''}`}
            onClick={() => setView('candidates')}
          >
            <Users className="nav-icon" />
            <span>Candidates Pool</span>
          </div>

          <div 
            className={`nav-item ${view === 'run-pipeline' ? 'active' : ''}`}
            onClick={() => setView('run-pipeline')}
          >
            <Play className="nav-icon" />
            <span>Run Pipeline</span>
          </div>

          <div 
            className={`nav-item ${view === 'shortlist' ? 'active' : ''}`}
            onClick={() => setView('shortlist')}
          >
            <ListOrdered className="nav-icon" />
            <span>Evaluation Shortlist</span>
          </div>

          <div 
            className={`nav-item ${view === 'settings' ? 'active' : ''}`}
            onClick={() => setView('settings')}
          >
            <SettingsIcon className="nav-icon" />
            <span>Settings</span>
          </div>
        </nav>

        <button 
          className="btn btn-secondary btn-sm"
          style={{ width: '100%', marginTop: '20px', display: 'flex', alignItems: 'center', gap: '6px' }}
          onClick={fetchData}
        >
          <RefreshCw size={14} />
          Sync Data
        </button>

        <div className="sidebar-footer">
          <span>v1.0.0 · Calipr AI</span>
        </div>
      </aside>

      {/* Main Panel Content */}
      <main className="main-content">
        {error && (
          <div className="glass-container" style={{ borderColor: 'var(--accent-coral)', background: 'rgba(201, 80, 46, 0.04)', display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px' }}>
            <ShieldAlert size={24} style={{ color: 'var(--accent-coral)' }} />
            <div>
              <h4 style={{ color: 'var(--accent-coral)' }}>Backend Server Offline</h4>
              <p style={{ fontSize: '13px', color: 'var(--text-body)' }}>{error}</p>
            </div>
          </div>
        )}

        {isLoading && candidates.length === 0 ? (
          <div className="loader-wrapper" style={{ minHeight: '80vh' }}>
            <div className="pulse-spinner" />
            <h3>Connecting to Calipr Server</h3>
            <p style={{ color: 'var(--text-muted)' }}>Fetching candidate pool profiles and history records...</p>
          </div>
        ) : (
          renderActiveView()
        )}
      </main>
    </div>
  );
}

export default App;
