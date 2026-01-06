import React from 'react';

function XAIDashboard({ predictions }) {
  const latestPred = predictions;
  const xai = latestPred?.xai?.grad_cam;

  return (
    <div className="xai-dashboard">
      <h2>Neural Interpretability Dashboard</h2>
      
      {xai ? (
        <>
          <div className="xai-section">
            <h3>Channel Importance (EEG Electrodes)</h3>
            <div className="channels-grid">
              {xai.channel_importance.map((imp, i) => (
                <div 
                  key={i} 
                  className="channel-box"
                  style={{ opacity: 0.3 + (imp * 0.7) }}
                  title={`${xai.channel_names[i]}: ${(imp * 100).toFixed(1)}%`}
                >
                  {xai.channel_names[i]}
                  <div className="importance-value">{(imp * 100).toFixed(0)}%</div>
                </div>
              ))}
            </div>
          </div>

          <div className="xai-section">
            <h3>Top Contributing Channels</h3>
            {latestPred.xai.top_channels.map((ch, i) => (
              <div key={i} className="channel-bar">
                <span>{ch.name}</span>
                <div className="bar">
                  <div className="fill" style={{ width: `${ch.importance * 100}%` }} />
                </div>
                <span>{(ch.importance * 100).toFixed(1)}%</span>
              </div>
            ))}
          </div>

          <div className="xai-section">
            <h3>Time Importance Heatmap</h3>
            <div className="heatmap">
              {xai.time_importance.map((val, i) => (
                <div 
                  key={i}
                  className="heatmap-cell"
                  style={{ 
                    backgroundColor: `rgba(0, 100, 200, ${val})`
                  }}
                  title={`t=${i*10}ms: ${(val*100).toFixed(0)}%`}
                />
              ))}
            </div>
            <p className="heatmap-label">Time progression (0ms to 3000ms)</p>
          </div>

          <div className="neuroscience-info">
            <h4>📌 Neuroscience Insight</h4>
            <p>The highlighted channels correspond to motor cortex regions:</p>
            <ul>
              <li><strong>C3/C4:</strong> Primary motor cortex (hand/arm)</li>
              <li><strong>Cz:</strong> Central midline (feet)</li>
              <li><strong>Pz:</strong> Parietal (sensorimotor)</li>
            </ul>
          </div>
        </>
      ) : (
        <div className="empty-state">No predictions yet. Start a session to see XAI insights.</div>
      )}
    </div>
  );
}

export default XAIDashboard;
