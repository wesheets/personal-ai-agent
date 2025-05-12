import React from 'react';

const LoopReplayExplainer = ({ explanationData, replaySteps }) => {
  if (!explanationData && (!replaySteps || replaySteps.length === 0)) {
    return <p>No replay or explanation data available.</p>;
  }

  return (
    <div style={{ border: '1px solid #ccc', padding: '16px', margin: '16px 0', borderRadius: '8px' }}>
      <h3>Loop Explanation & Replay</h3>
      
      {explanationData && (
        <div style={{ marginBottom: '20px' }}>
          <h4>Explanation Summary:</h4>
          <p><strong>Goal:</strong> {explanationData.goal || 'Not specified'}</p>
          <p><strong>Overall Summary:</strong> {explanationData.summary || 'No summary provided.'}</p>
          <p><strong>Key Agents Involved:</strong> {(explanationData.key_agents && explanationData.key_agents.join(', ')) || 'None listed.'}</p>
          <div>
            <strong>Major Decisions/Actions:</strong>
            {explanationData.decisions && explanationData.decisions.length > 0 ? (
              <ul>
                {explanationData.decisions.map((decision, index) => (
                  <li key={index}>{decision}</li>
                ))}
              </ul>
            ) : (
              <p>No major decisions recorded.</p>
            )}
          </div>
          <p><strong>Final Outcome:</strong> {explanationData.outcome || 'Not recorded.'}</p>
        </div>
      )}

      {replaySteps && replaySteps.length > 0 && (
        <div>
          <h4>Replay Steps:</h4>
          <ul style={{ listStyleType: 'none', paddingLeft: 0 }}>
            {replaySteps.map((step, index) => (
              <li key={index} style={{ borderBottom: '1px dashed #eee', paddingTop: '8px', paddingBottom: '8px' }}>
                <p><strong>Step {index + 1}: Agent - {step.agent || 'Unknown'}</strong></p>
                <p>Action/Observation: {step.action || step.observation || 'No details'}</p>
                {step.timestamp && <small>Timestamp: {new Date(step.timestamp).toLocaleString()}</small>}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default LoopReplayExplainer;

