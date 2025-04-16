import { useState } from 'react';

/**
 * Agent Loop Validation Test Script
 *
 * This script validates the agent loop functionality across all active agents
 * by sending test prompts and verifying the expected behaviors.
 */

// Test cases for different agent types
const testCases = [
  // Core Promethios OS Agents
  {
    agentId: 'Core.Forge',
    prompt: 'Hello.',
    followUp: "What's your name?",
    expectedBehavior: 'Identity + memory logging'
  },
  { agentId: 'OpsAgent', prompt: 'Scaffold a vertical.', expectedBehavior: 'Task delegation' },
  {
    agentId: 'ObserverAgent',
    prompt: 'Summarize what just happened.',
    expectedBehavior: 'Contextual reflection'
  },
  { agentId: 'MemoryAgent', prompt: 'Search: LifeTree', expectedBehavior: 'Memory match' },
  { agentId: 'HAL', prompt: 'Are there any safety protocols?', expectedBehavior: 'Safety logic' },
  { agentId: 'Ash', prompt: 'Test this agent loop.', expectedBehavior: 'Diagnostic response' },

  // Life Tree Agent
  {
    agentId: 'LifeTree',
    prompt: 'Prompt a reflection about my childhood.',
    expectedBehavior: 'Reflective journaling prompt'
  },

  // Site Plan Agent
  {
    agentId: 'SiteGen',
    prompt: 'Generate a draft site plan for 2 acres.',
    expectedBehavior: 'Returns layout/config draft'
  },

  // NEUREAL Agent
  {
    agentId: 'NEUREAL',
    prompt: "Splice a dream based on today's emotions.",
    expectedBehavior: 'Surreal or symbolic output'
  }
];

function AgentLoopValidator() {
  const [results, setResults] = useState([]);
  const [currentTest, setCurrentTest] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [logEntries, setLogEntries] = useState([]);

  // Function to run a single test
  const runTest = async (test) => {
    setCurrentTest(test);

    try {
      // Log test start
      const startLog = `Testing ${test.agentId} with prompt: "${test.prompt}"`;
      setLogEntries((prev) => [...prev, { type: 'info', message: startLog }]);

      // Make API call to agent
      const response = await fetch('/api/agent/delegate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_id: test.agentId,
          prompt: test.prompt,
          history: [] // Empty history for clean test
        })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      // Check memory logging
      const memoryResponse = await fetch('/api/memory', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });

      const memoryData = await memoryResponse.json();
      const memoryLogged = memoryData.some(
        (entry) => entry.agent_id === test.agentId && entry.content.includes(test.prompt)
      );

      // Determine test result
      const success = data.message && data.message.length > 0 && memoryLogged;

      // Add result
      setResults((prev) => [
        ...prev,
        {
          ...test,
          success,
          response: data.message || 'No response',
          memoryLogged,
          timestamp: new Date().toISOString()
        }
      ]);

      // Log test completion
      const resultLog = success
        ? `✅ ${test.agentId} test passed`
        : `❌ ${test.agentId} test failed`;
      setLogEntries((prev) => [
        ...prev,
        {
          type: success ? 'success' : 'error',
          message: resultLog,
          details: data.message
        }
      ]);

      // If there's a follow-up prompt, run it
      if (test.followUp) {
        // Wait a moment before sending follow-up
        await new Promise((resolve) => setTimeout(resolve, 2000));

        const followUpLog = `Sending follow-up to ${test.agentId}: "${test.followUp}"`;
        setLogEntries((prev) => [...prev, { type: 'info', message: followUpLog }]);

        const followUpResponse = await fetch('/api/agent/delegate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            agent_id: test.agentId,
            prompt: test.followUp,
            history: [
              { role: 'user', content: test.prompt },
              { role: 'assistant', content: data.message || 'No response' }
            ]
          })
        });

        if (!followUpResponse.ok) {
          throw new Error(`API error on follow-up: ${followUpResponse.status}`);
        }

        const followUpData = await followUpResponse.json();

        // Check if follow-up response references previous context
        const contextual =
          followUpData.message &&
          (followUpData.message.includes(test.prompt) ||
            followUpData.message.toLowerCase().includes('name'));

        // Update result with follow-up info
        setResults((prev) =>
          prev.map((r) =>
            r.timestamp === results[results.length - 1]?.timestamp
              ? {
                  ...r,
                  followUpResponse: followUpData.message || 'No response',
                  contextual
                }
              : r
          )
        );

        const followUpResultLog = contextual
          ? `✅ ${test.agentId} follow-up test passed (contextual response)`
          : `⚠️ ${test.agentId} follow-up test partial (non-contextual response)`;
        setLogEntries((prev) => [
          ...prev,
          {
            type: contextual ? 'success' : 'warning',
            message: followUpResultLog,
            details: followUpData.message
          }
        ]);
      }
    } catch (error) {
      console.error(`Error testing ${test.agentId}:`, error);

      // Log error
      setLogEntries((prev) => [
        ...prev,
        {
          type: 'error',
          message: `Error testing ${test.agentId}: ${error.message}`
        }
      ]);

      // Add failed result
      setResults((prev) => [
        ...prev,
        {
          ...test,
          success: false,
          error: error.message,
          timestamp: new Date().toISOString()
        }
      ]);
    }
  };

  // Function to run all tests
  const runAllTests = async () => {
    setIsRunning(true);
    setResults([]);
    setLogEntries([
      {
        type: 'info',
        message: `Starting agent loop validation at ${new Date().toLocaleString()}`
      }
    ]);

    // Run tests sequentially
    for (const test of testCases) {
      await runTest(test);
      // Add delay between tests to avoid rate limiting
      await new Promise((resolve) => setTimeout(resolve, 3000));
    }

    // Check overall results
    const passedTests = results.filter((r) => r.success).length;
    const totalTests = testCases.length;
    const successRate = Math.round((passedTests / totalTests) * 100);

    setLogEntries((prev) => [
      ...prev,
      {
        type: 'info',
        message: `Validation complete. ${passedTests}/${totalTests} tests passed (${successRate}%)`
      }
    ]);

    setIsRunning(false);
    setCurrentTest(null);
  };

  // Function to generate validation report
  const generateReport = () => {
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        totalTests: testCases.length,
        passedTests: results.filter((r) => r.success).length,
        failedTests: results.filter((r) => !r.success).length,
        successRate: Math.round((results.filter((r) => r.success).length / testCases.length) * 100)
      },
      results: results,
      logs: logEntries
    };

    // Save report to localStorage
    localStorage.setItem('agent_validation_report', JSON.stringify(report));

    // Also log to console for debugging
    console.log('Agent Validation Report:', report);

    return report;
  };

  return {
    results,
    logEntries,
    currentTest,
    isRunning,
    runAllTests,
    runTest,
    generateReport
  };
}

export default AgentLoopValidator;
