import React from 'react';

function ControlPanel({ predictions, onStart, onStop, isLive }) {
  const latestPred = predictions;
  const classNames = ['🖐️ Left Hand', '🖐️ Right Hand', '🦵 Both Feet', '👅 Tongue'];
  
  return (
    <div className="control-panel">
      <div className="prediction-card">
        <div className="prediction-class">
          {latestPred ? classNames[latestPred.predicted_class] : 'Waiting...'}
        </div>
        <div className="confidence-bar">
          <div 
            className="confidence-fill"
            style={{ width: `${(latestPred?.confidence || 0) * 100}%` }}
          />
        </div>
        <div className="confidence-text">
          Confidence: {latestPred ? (latestPred.confidence * 100).toFixed(1) : 0}%
        </div>
        <div className="uncertainty-text">
          Uncertainty: {latestPred ? (latestPred.uncertainty * 100).toFixed(2) : 0}%
        </div>
      </div>

      <div className="probabilities-card">
        <h3>Class Probabilities</h3>
        {latestPred && latestPred.probabilities.map((prob, i) => (
          <div key={i} className="prob-bar">
            <span>{classNames[i]}</span>
            <div className="bar">
              <div className="fill" style={{ width: `${prob * 100}%` }} />
            </div>
            <span>{(prob * 100).toFixed(1)}%</span>
          </div>
        ))}
      </div>

      <div className="controls">
        <button 
          className="btn btn-start" 
          onClick={onStart}
          disabled={isLive}
        >
          ▶️ START SESSION
        </button>
        <button 
          className="btn btn-stop" 
          onClick={onStop}
          disabled={!isLive}
        >
          ⏹️ STOP SESSION
        </button>
      </div>

      <div className="recent-predictions">
        <h3>Recent Predictions</h3>
        <div className="pred-list">
          {predictions.slice(0, 10).map((pred, i) => (
            <div key={i} className="pred-item">
              {classNames[pred.predicted_class]} - {(pred.confidence * 100).toFixed(0)}%
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default ControlPanel;
