import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import './App.css';

import ControlPanel from './components/ControlPanel';
import XAIDashboard from './components/XAIDashboard';
import SessionAnalysis from './components/SessionAnalysis';
import SubjectProfile from './components/SubjectProfile';
import MonitoringDash from './components/MonitoringDash';
import ExplainabilityPanel from './components/ExplainabilityPanel';

function App() {
  const [socket, setSocket] = useState(null);
  const [activeTab, setActiveTab] = useState('control');
  const [sessionId, setSessionId] = useState(null);
  const [userId, setUserId] = useState(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [predictions, setPredictions] = useState([]);

  useEffect(() => {
    // Connect to backend
    const newSocket = io('http://localhost:5000');
    
    newSocket.on('connect', () => {
      console.log('✅ Connected to server');
    });
    
    newSocket.on('prediction_result', (data) => {
      setPredictions(prev => [...prev, data].slice(-50));  // Keep last 50
    });
    
    setSocket(newSocket);
    
    return () => newSocket.close();
  }, []);

  const startSession = async (name, age, condition) => {
    try {
      // Create user
      const userRes = await fetch('http://localhost:5000/api/user/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, age, condition })
      });
      const userData = await userRes.json();
      const newUserId = userData.user_id;
      setUserId(newUserId);
      
      // Create session
      const sessionRes = await fetch('http://localhost:5000/api/session/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: newUserId })
      });
      const sessionData = await sessionRes.json();
      const newSessionId = sessionData.session_id;
      setSessionId(newSessionId);
      
      // Start streaming
      socket.emit('start_stream', { session_id: newSessionId });
      setIsStreaming(true);
    } catch (error) {
      console.error('Error starting session:', error);
    }
  };

  const stopSession = () => {
    if (socket && sessionId) {
      socket.emit('stop_stream', { session_id: sessionId });
      setIsStreaming(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🧠 Adaptive Motor Imagery BCI System</h1>
        <p>Real-time EEG Decoding with Explainable AI</p>
      </header>

      <nav className="tab-navigation">
        <button 
          className={`tab-btn ${activeTab === 'control' ? 'active' : ''}`}
          onClick={() => setActiveTab('control')}
        >
          🎮 Control Panel
        </button>
        <button 
          className={`tab-btn ${activeTab === 'xai' ? 'active' : ''}`}
          onClick={() => setActiveTab('xai')}
        >
          🔍 XAI Dashboard
        </button>
        <button 
          className={`tab-btn ${activeTab === 'analysis' ? 'active' : ''}`}
          onClick={() => setActiveTab('analysis')}
        >
          📊 Analysis
        </button>
        <button 
          className={`tab-btn ${activeTab === 'monitoring' ? 'active' : ''}`}
          onClick={() => setActiveTab('monitoring')}
        >
          🔧 Monitoring
        </button>
        <button 
          className={`tab-btn ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          👤 Profile
        </button>
      </nav>

      <main className="app-content">
        {activeTab === 'control' && (
          <ControlPanel 
            sessionId={sessionId}
            socket={socket}
            isStreaming={isStreaming}
            predictions={predictions}
            onStartSession={startSession}
            onStopSession={stopSession}
          />
        )}
        
        {activeTab === 'xai' && (
          <XAIDashboard predictions={predictions} />
        )}
        
        {activeTab === 'analysis' && sessionId && (
          <SessionAnalysis sessionId={sessionId} />
        )}
        
        {activeTab === 'monitoring' && (
          <MonitoringDash socket={socket} />
        )}
        
        {activeTab === 'profile' && (
          <SubjectProfile userId={userId} />
        )}
      </main>

      <footer className="app-footer">
        <p>Session ID: {sessionId || 'None'} | Status: {isStreaming ? '🔴 LIVE' : '⚫ IDLE'}</p>
      </footer>
    </div>
  );
}

export default App;