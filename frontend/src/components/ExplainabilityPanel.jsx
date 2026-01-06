import React from 'react';

function ExplainabilityPanel() {
  return (
    <div className="explainability-panel">
      <h2>Educational Resource</h2>
      
      <div className="edu-card">
        <h3>What is Motor Imagery (MI)?</h3>
        <p>
          Motor imagery is the mental simulation of movement without actual physical action. 
          When you imagine moving your right hand, your motor cortex activates similarly to 
          when you actually move it.
        </p>
      </div>

      <div className="edu-card">
        <h3>What is Grad-CAM?</h3>
        <p>
          Grad-CAM (Gradient-weighted Class Activation Map) shows which EEG channels 
          (electrodes) were most important for the model's prediction. This helps understand 
          if the AI is using the correct brain regions (e.g., C3/C4 for hands).
        </p>
      </div>

      <div className="edu-card">
        <h3>What is Uncertainty?</h3>
        <p>
          Uncertainty measures how confident the model is. High uncertainty means you should 
          repeat the trial. Low uncertainty means the prediction is reliable.
        </p>
      </div>

      <div className="edu-card">
        <h3>How to Improve Your MI Skills</h3>
        <ul>
          <li>Focus on kinesthetic imagery (feel the movement)</li>
          <li>Practice the same MI task repeatedly</li>
          <li>Watch the real-time feedback</li>
          <li>Build awareness of motor cortex activation</li>
        </ul>
      </div>
    </div>
  );
}

export default ExplainabilityPanel;
