import React from 'react';

function SubjectProfile({ userId }) {
  return (
    <div className="subject-profile">
      <h2>👤 Subject Profile</h2>
      
      {userId ? (
        <div className="profile-info">
          <div className="info-item">
            <h4>User ID:</h4>
            <p>{userId}</p>
          </div>
          
          <div className="info-item">
            <h4>Sessions:</h4>
            <p>View in Analysis tab</p>
          </div>
          
          <div className="info-item">
            <h4>Previous Results:</h4>
            <p>Historical data saved in database</p>
          </div>
        </div>
      ) : (
        <div className="placeholder">
          <p>No active profile. Start a session to create one.</p>
        </div>
      )}
    </div>
  );
}

export default SubjectProfile;