import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('control');
  const [socket, setSocket] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [isLive, setIsLive] = useState(false);
  const [backendHealth, setBackendHealth] = useState('disconnected');

  useEffect(() => {
    // Connect to backend
    const newSocket = io('http://localhost:5000', {
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5
    });

    newSocket.on('connect', () => {
      console.log('Connected to backend');
      setBackendHealth('connected');
    });

    newSocket.on('disconnect', () => {
      setBackendHealth('disconnected');
    });

    newSocket.on('prediction_update', (data) => {
      setPredictions(prev => [data, ...prev].slice(0, 50)); // Keep last 50
    });

    setSocket(newSocket);

    // Check backend health
    fetch('http://localhost:5000/api/health')
      .then(res => res.json())
      .then(data => setBackendHealth('healthy'))
      .catch(() => setBackendHealth('unhealthy'));

    return () => newSocket.close();
  }, []);

  const handleStartSession = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/sessions/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 1 })
      });
      const data = await res.json();
      setSessionId(data.session_id);
      setIsLive(true);
      
      // Start streaming
      if (socket) {
        socket.emit('start_stream', { session_id: data.session_id });
      }
    } catch (err) {
      console.error('Failed to start session:', err);
    }
  };

  const handleStopSession = async () => {
    if (!sessionId) return;
    
    try {
      const res = await fetch(`http://localhost:5000/api/sessions/${sessionId}/end`, {
        method: 'POST'
      });
      const data = await res.json();
      setIsLive(false);
      
      if (socket) {
        socket.emit('stop_stream', { session_id: sessionId });
      }
    } catch (err) {
      console.error('Failed to end session:', err);
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <h1>🧠 MI-BCI System</h1>
          <div className="header-status">
            <span className={`status-badge ${backendHealth === 'connected' ? 'connected' : 'disconnected'}`}>
              {backendHealth === 'connected' ? '🟢 LIVE' : '🔴 OFFLINE'}
            </span>
            {isLive && <span className="recording-badge">● RECORDING</span>}
          </div>
        </div>
      </header>

      {/* Tab Navigation */}
      <nav className="tab-nav">
        <button 
          className={`tab-btn ${activeTab === 'control' ? 'active' : ''}`}
          onClick={() => setActiveTab('control')}
        >
          🎮 Control
        </button>
        <button 
          className={`tab-btn ${activeTab === 'xai' ? 'active' : ''}`}
          onClick={() => setActiveTab('xai')}
        >
          🔍 XAI
        </button>
        <button 
          className={`tab-btn ${activeTab === 'analysis' ? 'active' : ''}`}
          onClick={() => setActiveTab('analysis')}
        >
          📊 Analysis
        </button>
        <button 
          className={`tab-btn ${activeTab === 'monitor' ? 'active' : ''}`}
          onClick={() => setActiveTab('monitor')}
        >
          🔧 Monitor
        </button>
        <button 
          className={`tab-btn ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          👤 Profile
        </button>
        <button 
          className={`tab-btn ${activeTab === 'education' ? 'active' : ''}`}
          onClick={() => setActiveTab('education')}
        >
          📚 Education
        </button>
      </nav>

      {/* Tab Content */}
      <main className="tab-content">
        {activeTab === 'control' && (
          <ControlPanel 
            predictions={predictions} 
            onStart={handleStartSession}
            onStop={handleStopSession}
            isLive={isLive}
          />
        )}
        {activeTab === 'xai' && (
          <XAIDashboard predictions={predictions} />
        )}
        {activeTab === 'analysis' && (
          <SessionAnalysis predictions={predictions} sessionId={sessionId} />
        )}
        {activeTab === 'monitor' && (
          <MonitoringDash backendHealth={backendHealth} />
        )}
        {activeTab === 'profile' && (
          <SubjectProfile sessionId={sessionId} />
        )}
        {activeTab === 'education' && (
          <ExplainabilityPanel />
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>Motor Imagery BCI System v1.0 | Enhanced IFNet with Explainability</p>
      </footer>
    </div>
  );
}

export default App;
