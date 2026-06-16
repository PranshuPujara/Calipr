import React, { useState, useEffect } from 'react';
import { Key, ShieldCheck, HelpCircle, Save, Check, Cpu, Zap } from 'lucide-react';

const LLM_OPTIONS = {
  groq: {
    name: 'Groq',
    description: 'Ultra-fast inference on open-source models',
    models: [
      { id: 'llama-3.1-70b-versatile', name: 'Llama 3.1 70B', desc: 'Best quality, tool-use capable' },
      { id: 'llama-3.3-70b-versatile', name: 'Llama 3.3 70B', desc: 'Latest Llama, improved reasoning' },
      { id: 'llama-3.1-8b-instant', name: 'Llama 3.1 8B', desc: 'Fastest, good for quick tasks' },
      { id: 'gemma2-9b-it', name: 'Gemma 2 9B', desc: 'Google open model, balanced' },
      { id: 'mixtral-8x7b-32768', name: 'Mixtral 8x7B', desc: 'MoE architecture, 32K context' },
    ]
  },
  gemini: {
    name: 'Gemini',
    description: 'Google AI with large context reasoning',
    models: [
      { id: 'gemini-2.0-flash', name: 'Gemini 2.0 Flash', desc: 'Latest, fast and capable' },
      { id: 'gemini-1.5-flash', name: 'Gemini 1.5 Flash', desc: 'Fast, cost-efficient' },
      { id: 'gemini-1.5-pro', name: 'Gemini 1.5 Pro', desc: 'Highest quality, 1M context' },
    ]
  }
};

const Settings = ({ backendUrl }) => {
  const [groqKey, setGroqKey] = useState('');
  const [geminiKey, setGeminiKey] = useState('');
  const [provider, setProvider] = useState('groq');
  const [selectedModel, setSelectedModel] = useState('llama-3.1-70b-versatile');
  
  const [isLoading, setIsLoading] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState('');
  const [testStatus, setTestStatus] = useState(''); // '', 'testing', 'success', 'failed'

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
          setSelectedModel(data.model_name || 'llama-3.1-70b-versatile');
        }
      } catch (e) {
        console.error("Failed to load settings from server:", e);
      }
    };
    fetchConfig();
  }, [backendUrl]);

  // When provider changes, set default model for that provider
  useEffect(() => {
    const models = LLM_OPTIONS[provider]?.models || [];
    if (models.length > 0 && !models.find(m => m.id === selectedModel)) {
      setSelectedModel(models[0].id);
    }
  }, [provider]);

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
          groq_api_key: groqKey === '****' ? null : groqKey,
          gemini_api_key: geminiKey === '****' ? null : geminiKey,
          llm_provider: provider,
          model_name: selectedModel
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

  const handleTestConnection = async () => {
    setTestStatus('testing');
    try {
      const res = await fetch(`${backendUrl}/api/config/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: provider,
          model_name: selectedModel
        }),
      });

      if (res.ok) {
        const data = await res.json();
        if (data.status === 'success') {
          setTestStatus('success');
        } else {
          setTestStatus('failed');
          setSaveError(data.error || 'LLM test failed.');
        }
      } else {
        setTestStatus('failed');
        const errData = await res.json();
        setSaveError(errData.detail || 'Connection test failed.');
      }
    } catch (err) {
      setTestStatus('failed');
      setSaveError(err.message || 'Cannot reach server.');
    }
    setTimeout(() => setTestStatus(''), 3000);
  };

  const currentModels = LLM_OPTIONS[provider]?.models || [];

  return (
    <div>
      <div className="page-header">
        <div className="page-title">
          <h1>System Settings</h1>
          <p>Configure API integrations, select your LLM engine, and choose the model.</p>
        </div>
      </div>

      <div className="glass-container" style={{ maxWidth: '700px' }}>
        <form onSubmit={handleSubmit}>
          {/* LLM Provider Selection */}
          <h3 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Cpu size={18} />
            LLM Engine Selection
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '24px' }}>
            {Object.entries(LLM_OPTIONS).map(([key, opt]) => (
              <div
                key={key}
                onClick={() => setProvider(key)}
                style={{
                  padding: '16px',
                  borderRadius: '12px',
                  border: provider === key ? '2px solid var(--accent-blue)' : '2px solid rgba(0,0,0,0.08)',
                  background: provider === key ? 'rgba(21, 108, 194, 0.06)' : 'rgba(0,0,0,0.02)',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
              >
                <div style={{ fontWeight: 700, fontSize: '15px', marginBottom: '4px', color: provider === key ? 'var(--accent-blue)' : 'var(--text-dark)' }}>
                  {opt.name}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                  {opt.description}
                </div>
              </div>
            ))}
          </div>

          {/* Model Selection */}
          <div className="form-group" style={{ marginBottom: '24px' }}>
            <label htmlFor="model-select">Model</label>
            <select
              id="model-select"
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
            >
              {currentModels.map(m => (
                <option key={m.id} value={m.id}>
                  {m.name} — {m.desc}
                </option>
              ))}
            </select>
          </div>

          <hr style={{ border: 'none', borderTop: '1px solid rgba(0,0,0,0.08)', margin: '24px 0' }} />

          {/* API Keys */}
          <h3 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Key size={18} />
            API Keys
          </h3>

          <div className="form-group">
            <label htmlFor="groq-key">
              Groq API Key
              {provider === 'groq' && <span style={{ color: 'var(--accent-blue)', fontSize: '11px', marginLeft: '8px' }}>● Active</span>}
            </label>
            <input 
              type="password" 
              id="groq-key" 
              value={groqKey}
              onChange={(e) => setGroqKey(e.target.value)}
              placeholder="gsk_..."
            />
            <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Get free key at <a href="https://console.groq.com" target="_blank" rel="noreferrer" style={{ color: 'var(--accent-blue)' }}>console.groq.com</a>
            </p>
          </div>

          <div className="form-group" style={{ marginBottom: '24px' }}>
            <label htmlFor="gemini-key">
              Gemini API Key
              {provider === 'gemini' && <span style={{ color: 'var(--accent-blue)', fontSize: '11px', marginLeft: '8px' }}>● Active</span>}
            </label>
            <input 
              type="password" 
              id="gemini-key" 
              value={geminiKey}
              onChange={(e) => setGeminiKey(e.target.value)}
              placeholder="AIzaSy..."
            />
            <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Get free key at <a href="https://aistudio.google.com/apikey" target="_blank" rel="noreferrer" style={{ color: 'var(--accent-blue)' }}>aistudio.google.com</a>
            </p>
          </div>

          {saveError && (
            <div style={{ color: 'var(--accent-coral)', fontSize: '13px', marginBottom: '20px' }}>
              {saveError}
            </div>
          )}

          {saveSuccess && (
            <div style={{ color: 'var(--accent-green)', fontSize: '13px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Check size={16} /> Configuration saved successfully!
            </div>
          )}

          <div style={{ display: 'flex', gap: '12px' }}>
            <button type="submit" className="btn btn-primary" disabled={isLoading} style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
              <Save size={16} />
              {isLoading ? "Saving..." : "Save Settings"}
            </button>
            <button 
              type="button" 
              className="btn btn-secondary" 
              onClick={handleTestConnection}
              disabled={testStatus === 'testing'}
              style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}
            >
              <Zap size={16} />
              {testStatus === 'testing' ? 'Testing...' : testStatus === 'success' ? '✓ Connected!' : testStatus === 'failed' ? '✕ Failed' : 'Test Connection'}
            </button>
          </div>
        </form>
      </div>

      {/* Active Config Summary */}
      <div className="glass-container" style={{ maxWidth: '700px', marginTop: '24px' }}>
        <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
          <Zap size={18} />
          Active Configuration
        </h4>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
          <div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>Provider</div>
            <div style={{ fontWeight: 600, fontSize: '14px' }}>{LLM_OPTIONS[provider]?.name || provider}</div>
          </div>
          <div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>Model</div>
            <div style={{ fontWeight: 600, fontSize: '14px' }}>{currentModels.find(m => m.id === selectedModel)?.name || selectedModel}</div>
          </div>
          <div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>API Key Status</div>
            <div style={{ fontWeight: 600, fontSize: '14px', color: (provider === 'groq' ? groqKey : geminiKey) ? 'var(--accent-green)' : 'var(--accent-coral)' }}>
              {(provider === 'groq' ? groqKey : geminiKey) ? '✓ Configured' : '✕ Missing'}
            </div>
          </div>
        </div>
      </div>

      {/* Compliance Note */}
      <div className="glass-container" style={{ maxWidth: '700px', marginTop: '24px', background: 'rgba(14, 161, 88, 0.03)', borderColor: 'rgba(14, 161, 88, 0.2)' }}>
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
