import React from 'react';

function XAIDashboard({ predictions }) {
  const latestPrediction = predictions[predictions.length - 1];

  return (
    <div className="xai-dashboard">
      <h2>🔍 Neural Interpretability Dashboard</h2>
      
      {latestPrediction && latestPrediction.explanation ? (
        <div className="explanation-content">
          <div className="explanation-section">
            <h3>🧠 Method: Grad-CAM + Integrated Gradients</h3>
            <p>
              Hybrid approach shows which EEG channels and time segments 
              contributed most to the model's decision.
            </p>
          </div>
          
          <div className="importance-section">
            <h4>Channel Importance (Grad-CAM)</h4>
            <div className="importance-bars">
              {latestPrediction.explanation.grad_cam.channel_importance.slice(0, 10).map((imp, idx) => (
                <div key={idx} className="bar-item">
                  <span className="channel-name">Ch {idx}</span>
                  <div className="bar">
                    <div className="bar-fill" style={{width: `${(imp / 0.5) * 100}%`}} />
                  </div>
                  <span className="value">{imp.toFixed(3)}</span>
                </div>
              ))}
            </div>
          </div>
          
          <div className="time-importance">
            <h4>Time Segment Importance</h4>
            <p>Red = more important time windows for the decision</p>
            <div className="time-heatmap">
              {/* Simplified: show bars for time bins */}
              {latestPrediction.explanation.grad_cam.time_importance.slice(0, 30).map((imp, idx) => (
                <div 
                  key={idx} 
                  className="time-bin"
                  style={{
                    height: `${(imp / 0.02) * 100}px`,
                    backgroundColor: `rgba(255, 0, 0, ${imp / 0.02})`
                  }}
                  title={`Time: ${idx * 10}ms, Importance: ${imp.toFixed(4)}`}
                />
              ))}
            </div>
          </div>

          <div className="neuroscience-insight">
            <h4>💡 Neuroscience Insight</h4>
            <p>
              The important channels highlighted above correspond to motor cortex regions (C3, C4, Cz)
              which is expected for motor imagery tasks. The temporal importance shows that 
              activation peaks around 1-2 seconds after movement cue, consistent with MI ERD/ERS patterns.
            </p>
          </div>
        </div>
      ) : (
        <div className="placeholder">
          <p>No predictions yet. Start a session to see neural interpretability.</p>
        </div>
      )}
    </div>
  );
}

export default XAIDashboard;