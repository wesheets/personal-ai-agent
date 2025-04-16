import React, { useState } from 'react';
import axios from 'axios';

const AgentCommandPanel = () => {
  const [activeTab, setActiveTab] = useState('memory');
  const [formData, setFormData] = useState({
    memory: {
      agent_id: '',
      memory_type: '',
      content: '',
      tags: ''
    },
    reflection: {
      agent_id: '',
      type: '',
      limit: 5
    },
    delegation: {
      from_agent: '',
      to_agent: '',
      task: ''
    }
  });
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleInputChange = (tab, field, value) => {
    setFormData({
      ...formData,
      [tab]: {
        ...formData[tab],
        [field]: value
      }
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      let endpoint = '';
      let payload = {};

      switch (activeTab) {
        case 'memory':
          endpoint = '/api/modules/memory/write';
          payload = {
            agent_id: formData.memory.agent_id,
            memory_type: formData.memory.memory_type,
            content: formData.memory.content,
            tags: formData.memory.tags
              .split(',')
              .map((tag) => tag.trim())
              .filter((tag) => tag)
          };
          break;
        case 'reflection':
          endpoint = '/api/modules/memory/reflect';
          payload = {
            agent_id: formData.reflection.agent_id,
            type: formData.reflection.type,
            limit: parseInt(formData.reflection.limit) || 5
          };
          break;
        case 'delegation':
          endpoint = '/api/modules/delegate';
          payload = {
            from_agent: formData.delegation.from_agent,
            to_agent: formData.delegation.to_agent,
            task: formData.delegation.task
          };
          break;
        default:
          throw new Error('Invalid tab selected');
      }

      const result = await axios.post(endpoint, payload);
      setResponse(result.data);
    } catch (err) {
      console.error(`Error in ${activeTab} operation:`, err);
      setError(err.response?.data?.message || err.message || 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const renderForm = () => {
    switch (activeTab) {
      case 'memory':
        return (
          <div className="space-y-4">
            <div>
              <label htmlFor="agent_id" className="block text-sm font-medium text-gray-700 mb-1">
                Agent ID *
              </label>
              <input
                type="text"
                id="agent_id"
                value={formData.memory.agent_id}
                onChange={(e) => handleInputChange('memory', 'agent_id', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., hal"
                required
              />
            </div>

            <div>
              <label htmlFor="memory_type" className="block text-sm font-medium text-gray-700 mb-1">
                Memory Type *
              </label>
              <input
                type="text"
                id="memory_type"
                value={formData.memory.memory_type}
                onChange={(e) => handleInputChange('memory', 'memory_type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., observation"
                required
              />
            </div>

            <div>
              <label htmlFor="tags" className="block text-sm font-medium text-gray-700 mb-1">
                Tags (comma separated)
              </label>
              <input
                type="text"
                id="tags"
                value={formData.memory.tags}
                onChange={(e) => handleInputChange('memory', 'tags', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., important, user-interaction"
              />
            </div>

            <div>
              <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-1">
                Content *
              </label>
              <textarea
                id="content"
                value={formData.memory.content}
                onChange={(e) => handleInputChange('memory', 'content', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                rows="4"
                placeholder="Memory content..."
                required
              />
            </div>
          </div>
        );

      case 'reflection':
        return (
          <div className="space-y-4">
            <div>
              <label
                htmlFor="reflection_agent_id"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Agent ID *
              </label>
              <input
                type="text"
                id="reflection_agent_id"
                value={formData.reflection.agent_id}
                onChange={(e) => handleInputChange('reflection', 'agent_id', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., hal"
                required
              />
            </div>

            <div>
              <label
                htmlFor="reflection_type"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Memory Type to Reflect On *
              </label>
              <input
                type="text"
                id="reflection_type"
                value={formData.reflection.type}
                onChange={(e) => handleInputChange('reflection', 'type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., observation"
                required
              />
            </div>

            <div>
              <label
                htmlFor="reflection_limit"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Memory Limit
              </label>
              <input
                type="number"
                id="reflection_limit"
                value={formData.reflection.limit}
                onChange={(e) => handleInputChange('reflection', 'limit', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                min="1"
                max="50"
              />
            </div>
          </div>
        );

      case 'delegation':
        return (
          <div className="space-y-4">
            <div>
              <label htmlFor="from_agent" className="block text-sm font-medium text-gray-700 mb-1">
                From Agent *
              </label>
              <input
                type="text"
                id="from_agent"
                value={formData.delegation.from_agent}
                onChange={(e) => handleInputChange('delegation', 'from_agent', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., hal"
                required
              />
            </div>

            <div>
              <label htmlFor="to_agent" className="block text-sm font-medium text-gray-700 mb-1">
                To Agent *
              </label>
              <input
                type="text"
                id="to_agent"
                value={formData.delegation.to_agent}
                onChange={(e) => handleInputChange('delegation', 'to_agent', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., ash"
                required
              />
            </div>

            <div>
              <label htmlFor="task" className="block text-sm font-medium text-gray-700 mb-1">
                Task *
              </label>
              <textarea
                id="task"
                value={formData.delegation.task}
                onChange={(e) => handleInputChange('delegation', 'task', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                rows="4"
                placeholder="Describe the task to delegate..."
                required
              />
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold mb-4">Agent Command Panel</h2>

      <div className="bg-white shadow rounded-xl overflow-hidden">
        <div className="flex border-b">
          <button
            className={`px-4 py-2 text-sm font-medium ${activeTab === 'memory' ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-500' : 'text-gray-500 hover:text-gray-700'}`}
            onClick={() => setActiveTab('memory')}
          >
            Memory Write
          </button>
          <button
            className={`px-4 py-2 text-sm font-medium ${activeTab === 'reflection' ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-500' : 'text-gray-500 hover:text-gray-700'}`}
            onClick={() => setActiveTab('reflection')}
          >
            Reflection Trigger
          </button>
          <button
            className={`px-4 py-2 text-sm font-medium ${activeTab === 'delegation' ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-500' : 'text-gray-500 hover:text-gray-700'}`}
            onClick={() => setActiveTab('delegation')}
          >
            Delegation
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4">
          {renderForm()}

          <div className="mt-4 flex justify-end">
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              disabled={loading}
            >
              {loading ? 'Processing...' : 'Submit'}
            </button>
          </div>
        </form>
      </div>

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
          <pre className="mt-2 whitespace-pre-wrap text-sm">
            {JSON.stringify(response, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default AgentCommandPanel;
