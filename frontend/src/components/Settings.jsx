import React, { useState, useEffect } from 'react';
import { Key, ShieldCheck, HelpCircle, Save, Check } from 'lucide-react';

const Settings = ({ backendUrl }) => {
  const [groqKey, setGroqKey] = useState('');
  const [geminiKey, setGeminiKey] = useState('');
  const [provider, setProvider] = useState('groq');
  
  const [isLoading, setIsLoading] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState('');

  // Fetch active settings on load
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const res = await fetch(`${backendUrl}/api/config`);
        if (res.ok) {
          const data = await res.json();
          setGroqKey(data.groq_api_key || '');
          setGeminiKey(data.gemini_api_key || '');
          setProvider(data.llm_provider || 'groq');
        }
      } catch (e) {
        console.error("Failed to load settings from server:", e);
      }
    };
    fetchConfig();
  }, [backendUrl]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setSaveError('');
    setSaveSuccess(false);

    try {
      const res = await fetch(`${backendUrl}/api/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          // If the key is "****", it means it's already set and unchanged, so we send null to keep the existing key
          groq_api_key: groqKey === '****' ? null : groqKey,
          gemini_api_key: geminiKey === '****' ? null : geminiKey,
          llm_provider: provider
        }),
      });

      if (!res.ok) {
        throw new Error('Failed to update configurations on the backend server.');
      }

      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2000);
    } catch (err) {
      setSaveError(err.message || 'Error saving settings.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <div className="page-title">
          <h1>System Settings</h1>
          <p>Configure API integrations, active LLM engines, and operational weights.</p>
        </div>
      </div>

      <div className="glass-container" style={{ maxWidth: '640px' }}>
        <form onSubmit={handleSubmit}>
          <h3 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Key size={18} />
            API Configurations
          </h3>

          <div className="form-group">
            <label htmlFor="provider">Default LLM Provider</label>
            <select 
              id="provider"
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
            >
              <option value="groq">Groq AI (Faster, Tool Use capability)</option>
              <option value="gemini">Gemini API (Large Context reasoning)</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="groq-key">Groq API Key</label>
            <input 
              type="password" 
              id="groq-key" 
              value={groqKey}
              onChange={(e) => setGroqKey(e.target.value)}
              placeholder="gsk_..."
            />
            <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Used for Phase 4 agentic re-ranking using Llama-3-70b-ToolUse.
            </p>
          </div>

          <div className="form-group" style={{ marginBottom: '24px' }}>
            <label htmlFor="gemini-key">Gemini API Key</label>
            <input 
              type="password" 
              id="gemini-key" 
              value={geminiKey}
              onChange={(e) => setGeminiKey(e.target.value)}
              placeholder="AIzaSy..."
            />
            <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Used for job description parsing and optional Gemini-based re-ranking.
            </p>
          </div>

          {saveError && (
            <div style={{ color: 'var(--accent-coral)', fontSize: '13px', marginBottom: '20px' }}>
              {saveError}
            </div>
          )}

          {saveSuccess && (
            <div style={{ color: 'var(--accent-green)', fontSize: '13px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Check size={16} /> Configuration saved and updated inside .env!
            </div>
          )}

          <button type="submit" className="btn btn-primary" disabled={isLoading} style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
            <Save size={16} />
            {isLoading ? "Saving Configurations..." : "Save Settings"}
          </button>
        </form>
      </div>

      {/* Safety & Compliance info block */}
      <div className="glass-container" style={{ maxWidth: '640px', marginTop: '24px', background: 'rgba(14, 161, 88, 0.03)', borderColor: 'rgba(14, 161, 88, 0.2)' }}>
        <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-green)', marginBottom: '8px' }}>
          <ShieldCheck size={18} />
          Compliance & Safety Note
        </h4>
        <p style={{ fontSize: '13px', color: 'var(--text-body)', lineHeight: 1.6 }}>
          Calipr is designed with strict data privacy guidelines. API keys are saved locally inside your system's private <code>.env</code> file. No candidate data, resume text, or credentials are sent to external third-party servers except for processing via your chosen LLM endpoint.
        </p>
      </div>
    </div>
  );
};

export default Settings;
