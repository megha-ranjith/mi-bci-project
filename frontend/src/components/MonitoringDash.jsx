import React, { useState, useEffect } from 'react';

function MonitoringDash({ socket }) {
  const [health, setHealth] = useState(null);
  const [latency, setLatency] = useState(0);

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const checkHealth = async () => {
    try {
      const start = Date.now();
      const res = await fetch('http://localhost:5000/api/health');
      const data = await res.json();
      const elapsed = Date.now() - start;
      
      setHealth(data);
      setLatency(elapsed);
    } catch (error) {
      console.error('Health check failed:', error);
    }
  };

  return (
    <div className="monitoring-dash">
      <h2>🔧 System Monitoring Dashboard</h2>
      
      {health && (
        <div className="monitoring-cards">
          <div className="monitor-card">
            <h4>Server Status</h4>
            <p className={`status ${health.status === 'healthy' ? 'healthy' : 'error'}`}>
              {health.status.toUpperCase()}
            </p>
          </div>
          
          <div className="monitor-card">
            <h4>Processing Device</h4>
            <p>{health.device}</p>
          </div>
          
          <div className="monitor-card">
            <h4>Model Status</h4>
            <p className={health.model_loaded ? 'loaded' : 'error'}>
              {health.model_loaded ? '✅ Loaded' : '❌ Not Loaded'}
            </p>
          </div>
          
          <div className="monitor-card">
            <h4>Server Latency</h4>
            <p>{latency}ms</p>
          </div>
        </div>
      )}

      <div className="system-info">
        <h4>💾 System Information</h4>
        <ul>
          <li>Backend: Flask + PyTorch</li>
          <li>Frontend: React</li>
          <li>Database: SQLite</li>
          <li>Real-time: WebSocket</li>
          <li>XAI Methods: Grad-CAM, Integrated Gradients</li>
        </ul>
      </div>
    </div>
  );
}

export default MonitoringDash;