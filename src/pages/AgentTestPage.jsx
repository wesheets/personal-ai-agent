import React from 'react';
import { Routes, Route } from 'react-router-dom';
import AgentValidationPanel from '../components/AgentValidationPanel';

/**
 * AgentTestPage component
 * 
 * Page for testing and validating agent loop functionality
 */
const AgentTestPage = () => {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Agent Loop Test</h1>
      
      <div className="mb-6">
        <p className="text-gray-700">
          This page allows you to validate the cognition + memory loop across all active agents.
          Run the tests to ensure all agents are responding correctly and maintaining memory context.
        </p>
      </div>
      
      <AgentValidationPanel />
    </div>
  );
};

export default AgentTestPage;
