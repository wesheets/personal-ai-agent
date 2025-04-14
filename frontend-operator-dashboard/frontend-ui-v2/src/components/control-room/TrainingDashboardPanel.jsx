import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TrainingDashboardPanel = () => {
  const [trainingLogs, setTrainingLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTrainingHistory();
  }, []);

  const fetchTrainingHistory = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/modules/train/history?limit=25');
      if (response.data.status === 'ok') {
        setTrainingLogs(response.data.history || []);
      } else {
        setError('Failed to fetch training logs');
      }
    } catch (err) {
      setError(`Error: ${err.message}`);
      console.error('Failed to fetch training history:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch (e) {
      return timestamp;
    }
  };

  const truncateSummary = (summary) => {
    if (!summary) return "No summary available";
    return summary.length > 200 ? `${summary.substring(0, 200)}...` : summary;
  };

  const handleRetrain = async (agentId, goal, tags) => {
    // This would be implemented in the future to trigger retraining
    alert(`Retraining ${agentId} with goal: ${goal}`);
  };

  const handleExecuteStaged = async (trainingLogId) => {
    try {
      setLoading(true);
      const response = await axios.post('/api/modules/train/execute_staged', {
        training_log_id: trainingLogId
      });
      
      if (response.data.status === 'ok') {
        alert('Staged training executed successfully');
        fetchTrainingHistory(); // Refresh the list
      } else {
        setError('Failed to execute staged training');
      }
    } catch (err) {
      setError(`Error: ${err.message}`);
      console.error('Failed to execute staged training:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-gray-600">Loading training history...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        <p>{error}</p>
        <button 
          onClick={fetchTrainingHistory}
          className="mt-2 bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-2 rounded text-sm"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white shadow-md rounded-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Training History</h2>
        <button 
          onClick={fetchTrainingHistory}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Refresh
        </button>
      </div>

      {trainingLogs.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No training logs found. Start training agents to see history here.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white">
            <thead className="bg-gray-100">
              <tr>
                <th className="py-2 px-4 border-b text-left">Agent</th>
                <th className="py-2 px-4 border-b text-left">Goal</th>
                <th className="py-2 px-4 border-b text-left">Tags</th>
                <th className="py-2 px-4 border-b text-left">Memories</th>
                <th className="py-2 px-4 border-b text-left">Summary</th>
                <th className="py-2 px-4 border-b text-left">Time</th>
                <th className="py-2 px-4 border-b text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {trainingLogs.map((log) => (
                <tr key={log.training_log_id} className="hover:bg-gray-50">
                  <td className="py-2 px-4 border-b">{log.agent_id}</td>
                  <td className="py-2 px-4 border-b">{log.goal}</td>
                  <td className="py-2 px-4 border-b">{log.tags ? log.tags.join(', ') : ''}</td>
                  <td className="py-2 px-4 border-b">{log.memories_written}</td>
                  <td className="py-2 px-4 border-b max-w-xs truncate">{truncateSummary(log.summary)}</td>
                  <td className="py-2 px-4 border-b">{formatTimestamp(log.timestamp)}</td>
                  <td className="py-2 px-4 border-b">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleRetrain(log.agent_id, log.goal, log.tags)}
                        className="bg-green-500 hover:bg-green-700 text-white text-xs py-1 px-2 rounded"
                      >
                        Re-train
                      </button>
                      
                      {log.staged && (
                        <button
                          onClick={() => handleExecuteStaged(log.training_log_id)}
                          className="bg-purple-500 hover:bg-purple-700 text-white text-xs py-1 px-2 rounded"
                        >
                          Execute Staged
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default TrainingDashboardPanel;
