import React, { useState, useEffect } from 'react';

const EmotionStateViewer = () => {
  const [emotionState, setEmotionState] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchEmotionState = async () => {
      try {
        setIsLoading(true);
        // Assuming an API endpoint /api/emotion_state that returns JSON like: 
        // { "current_emotion": "neutral", "intensity": 0.5, "tendencies": ["calm", "focused"] }
        const response = await fetch('/api/emotion_state');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setEmotionState(data);
        setError(null);
      } catch (err) {
        setError(err.message);
        setEmotionState(null);
      } finally {
        setIsLoading(false);
      }
    };

    fetchEmotionState();
    // Optionally, set up an interval to periodically refresh the emotion state
    const intervalId = setInterval(fetchEmotionState, 30000); // Refresh every 30 seconds

    return () => clearInterval(intervalId); // Cleanup interval on component unmount
  }, []);

  if (isLoading) {
    return <div className="p-4 bg-gray-800 rounded-lg shadow text-white">Loading Emotion State...</div>;
  }

  if (error) {
    return <div className="p-4 bg-red-700 rounded-lg shadow text-white">Error fetching emotion state: {error}</div>;
  }

  if (!emotionState) {
    return <div className="p-4 bg-gray-800 rounded-lg shadow text-white">No emotion state data available.</div>;
  }

  // Basic visualization - can be enhanced with charts or more graphical elements
  return (
    <div className="p-4 bg-gray-700 rounded-lg shadow text-white">
      <h3 className="text-lg font-semibold mb-2">Current Emotional State</h3>
      <p><strong>Emotion:</strong> {emotionState.current_emotion || 'N/A'}</p>
      <p><strong>Intensity:</strong> {emotionState.intensity !== undefined ? emotionState.intensity.toFixed(2) : 'N/A'}</p>
      {emotionState.tendencies && (
        <p><strong>Tendencies:</strong> {emotionState.tendencies.join(', ') || 'None'}</p>
      )}
      {/* Placeholder for more advanced visualization */}
      {/* e.g., <EmotionChart data={emotionState} /> */}
    </div>
  );
};

export default EmotionStateViewer;

