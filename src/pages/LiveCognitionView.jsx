import React from 'react';
import JustificationGraphViewer from '../components/visualization/JustificationGraphViewer';
import EmotionStateViewer from '../components/visualization/EmotionStateViewer'; // Import the new component
import ReflectionThreadViewer from '../components/narrative/ReflectionThreadViewer'; // Assuming this might be used or integrated later

const LiveCognitionView = () => {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>Live Cognition View</h1>
      <p>This page displays various aspects of the agent's cognitive processes, including emotional state, justifications, and reflection threads.</p>
      
      <section style={{ marginTop: '30px', marginBottom: '30px', padding: '20px', border: '1px solid #eee', borderRadius: '8px', backgroundColor: '#f9f9f9' }}>
        <h2>Current Emotional State</h2>
        <EmotionStateViewer />
      </section>

      <section style={{ marginTop: '30px', marginBottom: '30px', padding: '20px', border: '1px solid #eee', borderRadius: '8px', backgroundColor: '#f9f9f9' }}>
        <h2>Agent Justification Graph</h2>
        <JustificationGraphViewer />
      </section>

      <section style={{ marginTop: '30px', marginBottom: '30px', padding: '20px', border: '1px solid #eee', borderRadius: '8px', backgroundColor: '#f9f9f9' }}>
        <h2>Reflection Thread</h2>
        {/* Assuming ReflectionThreadViewer fetches its own data or is passed data */}
        <ReflectionThreadViewer /> 
      </section>
      
      <section style={{ marginTop: '30px', marginBottom: '30px', padding: '20px', border: '1px solid #eee', borderRadius: '8px', backgroundColor: '#f9f9f9' }}>
        <h2>Other Cognitive Data</h2>
        <p>Other cognitive data displays can be integrated here as developed.</p>
      </section>
    </div>
  );
};

export default LiveCognitionView;

