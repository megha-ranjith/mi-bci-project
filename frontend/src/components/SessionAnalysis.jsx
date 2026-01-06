import React, { useState, useEffect } from 'react';

function SessionAnalysis({ sessionId }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSessionStats();
    const interval = setInterval(fetchSessionStats, 5000);  // Refresh every 5s
    return () => clearInterval(interval);
  }, [sessionId]);

  const fetchSessionStats = async () => {
    try {
      const res = await fetch(`http://localhost:5000/api/session/${sessionId}/stats`);
      const data = await res.json();
      setStats(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="session-analysis">
      <h2>📊 Session Analysis & Learning Curves</h2>
      
      {stats && (
        <div className="stats-container">
          <div className="stat-card">
            <h3>Total Trials</h3>
            <p className="stat-value">{stats.total_trials}</p>
          </div>
          
          <div className="stat-card">
            <h3>Correct Predictions</h3>
            <p className="stat-value">{stats.correct}</p>
          </div>
          
          <div className="stat-card">
            <h3>Overall Accuracy</h3>
            <p className="stat-value">{(stats.accuracy * 100).toFixed(1)}%</p>
            <div className="accuracy-bar">
              <div className="accuracy-fill" style={{width: `${stats.accuracy * 100}%`}} />
            </div>
          </div>
        </div>
      )}

      <div className="learning-curve-placeholder">
        <h4>Learning Curve Over Time</h4>
        <p>(Accuracy should improve with more trials and user practice)</p>
        <svg className="learning-curve" width="600" height="300">
          <line x1="50" y1="250" x2="550" y2="250" stroke="#ccc" />
          <line x1="50" y1="250" x2="50" y2="50" stroke="#ccc" />
          <text x="300" y="290" textAnchor="middle">Trial Number</text>
          <text x="20" y="150" textAnchor="middle">Accuracy (%)</text>
        </svg>
      </div>
    </div>
  );
}

export default SessionAnalysis;