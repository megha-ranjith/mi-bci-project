import React from 'react';

function ExplainabilityPanel() {
  return (
    <div className="explainability-panel">
      <h2>📚 Explainability & Education</h2>
      
      <div className="education-content">
        <section>
          <h3>What is Grad-CAM?</h3>
          <p>
            Class Activation Mapping highlights which EEG channels (electrodes) 
            were most important for the model's decision. Brighter colors = more important.
          </p>
        </section>

        <section>
          <h3>What is Integrated Gradients?</h3>
          <p>
            This method shows how each part of the signal (channel × time) 
            contributed to the prediction by integrating gradients from baseline.
          </p>
        </section>

        <section>
          <h3>Why is this important for patients?</h3>
          <ul>
            <li>Therapists can see which brain areas are activating</li>
            <li>Feedback: "Your motor cortex is activating well"</li>
            <li>Guides neurofeedback training</li>
            <li>Builds confidence through transparency</li>
          </ul>
        </section>

        <section>
          <h3>Motor Imagery Brain Regions</h3>
          <ul>
            <li><strong>C3, C4:</strong> Central motor cortex</li>
            <li><strong>CP3, CP4:</strong> Parietal motor regions</li>
            <li><strong>Cz, CPz:</strong> Midline motor areas</li>
            <li><strong>P3, P4:</strong> Parietal areas</li>
          </ul>
        </section>
      </div>
    </div>
  );
}

export default ExplainabilityPanel;