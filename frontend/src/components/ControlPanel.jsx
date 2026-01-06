import React, { useState } from 'react';

function ControlPanel({ sessionId, socket, isStreaming, predictions, onStartSession, onStopSession }) {
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [condition, setCondition] = useState('');

  const handleStart = () => {
    if (name && age) {
      onStartSession(name, age, condition);
    }
  };

  const latestPrediction = predictions[predictions.length - 1];
  const classNames = {
    0: 'Left Hand',
    1: 'Right Hand',
    2: 'Both Feet',
    3: 'Tongue'
  };

  return (
    <div className="control-panel">
      <h2>🎮 Real-Time BCI Control Panel</h2>
      
      {!isStreaming ? (
        <div className="session-setup">
          <div className="form-group">
            <label>Subject Name:</label>
            <input 
              type="text" 
              value={name} 
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter name"
            />
          </div>
          
          <div className="form-group">
            <label>Age:</label>
            <input 
              type="number" 
              value={age} 
              onChange={(e) => setAge(e.target.value)}
              placeholder="Enter age"
            />
          </div>
          
          <div className="form-group">
            <label>Condition (optional):</label>
            <select value={condition} onChange={(e) => setCondition(e.target.value)}>
              <option value="">Healthy</option>
              <option value="stroke">Stroke Patient</option>
              <option value="spinal">Spinal Cord Injury</option>
              <option value="other">Other</option>
            </select>
          </div>
          
          <button className="btn-primary" onClick={handleStart}>
            ▶️ Start Session
          </button>
        </div>
      ) : (
        <div className="session-active">
          <div className="prediction-display">
            {latestPrediction && (
              <>
                <div className="prediction-class">
                  <h3>{classNames[latestPrediction.predicted_class]}</h3>
                  <div className="confidence-bar">
                    <div 
                      className="confidence-fill"
                      style={{width: `${latestPrediction.confidence * 100}%`}}
                    />
                  </div>
                  <p>Confidence: {(latestPrediction.confidence * 100).toFixed(1)}%</p>
                </div>
              </>
            )}
          </div>
          
          <div className="prediction-history">
            <h3>Recent Predictions:</h3>
            <div className="history-list">
              {predictions.slice(-10).reverse().map((pred, idx) => (
                <div key={idx} className="history-item">
                  <span>{classNames[pred.predicted_class]}</span>
                  <span className="confidence">{(pred.confidence * 100).toFixed(0)}%</span>
                </div>
              ))}
            </div>
          </div>
          
          <button className="btn-danger" onClick={onStopSession}>
            ⏹️ Stop Session
          </button>
        </div>
      )}
    </div>
  );
}

export default ControlPanel;