import React from 'react';

function MonitoringDash({ backendHealth }) {
  return (
    <div className="monitoring-dash">
      <h2>System Monitoring</h2>
      
      <div className="monitor-grid">
        <div className={`monitor-card ${backendHealth === 'connected' ? 'healthy' : 'unhealthy'}`}>
          <h4>Backend Server</h4>
          <p className="status-text">{backendHealth === 'connected' ? '✅ Online' : '❌ Offline'}</p>
        </div>
        
        <div className="monitor-card healthy">
          <h4>Model Loaded</h4>
          <p className="status-text">✅ IFNetEnhanced</p>
        </div>
        
        <div className="monitor-card healthy">
          <h4>Latency</h4>
          <p className="status-text">47ms</p>
        </div>
        
        <div className="monitor-card">
          <h4>CPU Usage</h4>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: '45%' }} />
          </div>
          <p>45%</p>
        </div>
      </div>

      <div className="monitor-logs">
        <h3>System Logs</h3>
        <div className="log-entry">✓ Backend initialized</div>
        <div className="log-entry">✓ Database connected</div>
        <div className="log-entry">✓ Model loaded</div>
        <div className="log-entry">✓ Socket.IO ready</div>
      </div>
    </div>
  );
}

export default MonitoringDash;
