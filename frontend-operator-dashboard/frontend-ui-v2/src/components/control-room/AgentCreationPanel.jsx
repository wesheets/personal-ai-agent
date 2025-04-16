import React, { useState } from 'react';
import axios from 'axios';

const AgentCreationPanel = () => {
  const [formData, setFormData] = useState({
    agent_id: '',
    description: '',
    traits: ''
  });
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleInputChange = (field, value) => {
    setFormData({
      ...formData,
      [field]: value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResponse(null);

    // Validate required fields
    if (!formData.agent_id) {
      setError('Agent ID is required');
      setLoading(false);
      return;
    }

    try {
      // Parse traits from comma-separated string to array
      const traits = formData.traits
        .split(',')
        .map((trait) => trait.trim())
        .filter((trait) => trait);

      const payload = {
        agent_id: formData.agent_id,
        description: formData.description,
        traits: traits
      };

      const result = await axios.post('/api/modules/agent/create', payload);
      setResponse(result.data);

      // Clear form on success
      setFormData({
        agent_id: '',
        description: '',
        traits: ''
      });
    } catch (err) {
      console.error('Error creating agent:', err);
      setError(err.response?.data?.message || err.message || 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold mb-4">Create New Agent</h2>

      <form onSubmit={handleSubmit} className="bg-white shadow rounded-xl p-4">
        <div className="space-y-4">
          <div>
            <label htmlFor="agent_id" className="block text-sm font-medium text-gray-700 mb-1">
              Agent ID *
            </label>
            <input
              type="text"
              id="agent_id"
              value={formData.agent_id}
              onChange={(e) => handleInputChange('agent_id', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="e.g., shiva"
              required
            />
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              id="description"
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              rows="3"
              placeholder="Describe the agent's purpose and personality..."
            />
          </div>

          <div>
            <label htmlFor="traits" className="block text-sm font-medium text-gray-700 mb-1">
              Traits (comma separated)
            </label>
            <input
              type="text"
              id="traits"
              value={formData.traits}
              onChange={(e) => handleInputChange('traits', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="e.g., creative, reflective, philosophical"
            />
          </div>
        </div>

        <div className="mt-4 flex justify-end">
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            disabled={loading}
          >
            {loading ? 'Creating...' : 'Create Agent'}
          </button>
        </div>
      </form>

      {error && (
        <div
          className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative"
          role="alert"
        >
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {response && (
        <div
          className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative"
          role="alert"
        >
          <strong className="font-bold">Success: </strong>
          <span className="block sm:inline">
            Agent "{response.agent_id || formData.agent_id}" has been created successfully!
          </span>
          <pre className="mt-2 whitespace-pre-wrap text-sm">
            {JSON.stringify(response, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default AgentCreationPanel;
