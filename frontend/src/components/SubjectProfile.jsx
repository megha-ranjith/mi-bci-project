import React from 'react';

function SubjectProfile({ sessionId }) {
  return (
    <div className="subject-profile">
      <h2>Subject Profile</h2>
      
      <div className="profile-card">
        <h3>User Information</h3>
        <p><strong>Name:</strong> Test Subject</p>
        <p><strong>ID:</strong> 1</p>
        <p><strong>Age:</strong> 25</p>
        <p><strong>Condition:</strong> Healthy</p>
      </div>

      <div className="profile-card">
        <h3>Current Session</h3>
        <p><strong>Session ID:</strong> {sessionId || 'None'}</p>
        <p><strong>Status:</strong> {sessionId ? 'Active' : 'Idle'}</p>
      </div>

      <div className="profile-card">
        <h3>Session History</h3>
        <div className="history-list">
          <div className="history-item">Session 5 - 85% accuracy</div>
          <div className="history-item">Session 4 - 82% accuracy</div>
          <div className="history-item">Session 3 - 78% accuracy</div>
        </div>
      </div>
    </div>
  );
}

export default SubjectProfile;
