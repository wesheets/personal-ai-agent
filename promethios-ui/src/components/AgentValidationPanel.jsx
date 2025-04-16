import React, { useState, useEffect } from 'react';
import AgentLoopValidator from '../utils/AgentLoopValidator';

/**
 * AgentValidationPanel component
 *
 * UI for running agent loop validation tests and displaying results
 */
const AgentValidationPanel = () => {
  const validator = AgentLoopValidator();
  const [showReport, setShowReport] = useState(false);

  // Load previous report if available
  useEffect(() => {
    const savedReport = localStorage.getItem('agent_validation_report');
    if (savedReport) {
      try {
        const report = JSON.parse(savedReport);
        if (report.results && report.results.length > 0) {
          setShowReport(true);
        }
      } catch (e) {
        console.error('Failed to parse saved validation report:', e);
      }
    }
  }, []);

  const handleRunTests = () => {
    validator.runAllTests();
  };

  const handleGenerateReport = () => {
    validator.generateReport();
    setShowReport(true);
  };

  const handleClearResults = () => {
    localStorage.removeItem('agent_validation_report');
    window.location.reload();
  };

  return (
    <div className="p-4 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Agent Loop Validation</h1>

      <div className="mb-6 bg-gray-100 p-4 rounded-lg">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Test Controls</h2>
          <div className="space-x-2">
            <button
              onClick={handleRunTests}
              disabled={validator.isRunning}
              className={`px-4 py-2 rounded ${validator.isRunning ? 'bg-gray-400' : 'bg-blue-600 text-white hover:bg-blue-700'}`}
            >
              {validator.isRunning ? 'Testing...' : 'Run All Tests'}
            </button>
            <button
              onClick={handleGenerateReport}
              disabled={validator.isRunning || validator.results.length === 0}
              className={`px-4 py-2 rounded ${validator.isRunning || validator.results.length === 0 ? 'bg-gray-400' : 'bg-green-600 text-white hover:bg-green-700'}`}
            >
              Generate Report
            </button>
            <button
              onClick={handleClearResults}
              className="px-4 py-2 rounded bg-red-600 text-white hover:bg-red-700"
            >
              Clear Results
            </button>
          </div>
        </div>

        {validator.currentTest && (
          <div className="bg-blue-50 p-3 rounded border border-blue-200 mb-4">
            <p className="font-medium">
              Currently testing: <span className="font-bold">{validator.currentTest.agentId}</span>
            </p>
            <p className="text-sm">Prompt: "{validator.currentTest.prompt}"</p>
            <p className="text-sm">Expected: {validator.currentTest.expectedBehavior}</p>
          </div>
        )}

        <div className="h-64 overflow-y-auto bg-black text-green-400 p-3 rounded font-mono text-sm">
          {validator.logEntries.length === 0 ? (
            <p className="text-gray-500">Logs will appear here during testing...</p>
          ) : (
            validator.logEntries.map((log, index) => (
              <div
                key={index}
                className={`mb-1 ${
                  log.type === 'error'
                    ? 'text-red-400'
                    : log.type === 'success'
                      ? 'text-green-400'
                      : log.type === 'warning'
                        ? 'text-yellow-400'
                        : 'text-blue-400'
                }`}
              >
                <span className="opacity-70">[{new Date().toLocaleTimeString()}]</span>{' '}
                {log.message}
                {log.details && (
                  <div className="pl-6 text-xs opacity-80 mt-1 mb-2">{log.details}</div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {showReport && (
        <div className="mb-6 bg-white p-4 rounded-lg border border-gray-200">
          <h2 className="text-xl font-semibold mb-4">Validation Report</h2>

          {(() => {
            try {
              const report = JSON.parse(localStorage.getItem('agent_validation_report') || '{}');
              if (!report.summary) return <p>No report data available</p>;

              return (
                <>
                  <div className="grid grid-cols-4 gap-4 mb-6">
                    <div className="bg-gray-100 p-3 rounded">
                      <p className="text-sm text-gray-600">Total Tests</p>
                      <p className="text-2xl font-bold">{report.summary.totalTests}</p>
                    </div>
                    <div className="bg-green-100 p-3 rounded">
                      <p className="text-sm text-gray-600">Passed</p>
                      <p className="text-2xl font-bold text-green-700">
                        {report.summary.passedTests}
                      </p>
                    </div>
                    <div className="bg-red-100 p-3 rounded">
                      <p className="text-sm text-gray-600">Failed</p>
                      <p className="text-2xl font-bold text-red-700">
                        {report.summary.failedTests}
                      </p>
                    </div>
                    <div className="bg-blue-100 p-3 rounded">
                      <p className="text-sm text-gray-600">Success Rate</p>
                      <p className="text-2xl font-bold text-blue-700">
                        {report.summary.successRate}%
                      </p>
                    </div>
                  </div>

                  <h3 className="text-lg font-semibold mb-2">Test Results</h3>
                  <div className="overflow-x-auto">
                    <table className="min-w-full bg-white">
                      <thead className="bg-gray-100">
                        <tr>
                          <th className="py-2 px-4 text-left">Agent ID</th>
                          <th className="py-2 px-4 text-left">Prompt</th>
                          <th className="py-2 px-4 text-left">Expected</th>
                          <th className="py-2 px-4 text-left">Status</th>
                          <th className="py-2 px-4 text-left">Memory</th>
                        </tr>
                      </thead>
                      <tbody>
                        {report.results.map((result, index) => (
                          <tr key={index} className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                            <td className="py-2 px-4 font-medium">{result.agentId}</td>
                            <td className="py-2 px-4 text-sm">{result.prompt}</td>
                            <td className="py-2 px-4 text-sm">{result.expectedBehavior}</td>
                            <td className="py-2 px-4">
                              <span
                                className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                                  result.success
                                    ? 'bg-green-100 text-green-800'
                                    : 'bg-red-100 text-red-800'
                                }`}
                              >
                                {result.success ? 'PASSED' : 'FAILED'}
                              </span>
                            </td>
                            <td className="py-2 px-4">
                              {result.memoryLogged !== undefined && (
                                <span
                                  className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                                    result.memoryLogged
                                      ? 'bg-green-100 text-green-800'
                                      : 'bg-red-100 text-red-800'
                                  }`}
                                >
                                  {result.memoryLogged ? 'LOGGED' : 'NOT LOGGED'}
                                </span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              );
            } catch (e) {
              console.error('Error parsing report:', e);
              return <p className="text-red-600">Error loading report data</p>;
            }
          })()}
        </div>
      )}

      <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
        <h2 className="text-lg font-semibold mb-2">Loop Validation Criteria</h2>
        <ul className="list-disc pl-5 space-y-1">
          <li>GPT responses are contextual and not fallback</li>
          <li>Logs appear in /api/memory for each task/delegation</li>
          <li>
            Delegation events like:
            <pre className="bg-gray-100 p-2 rounded mt-1 text-xs">
              LOG: Core.Forge delegated task to OpsAgent
            </pre>
            <pre className="bg-gray-100 p-2 rounded mt-1 text-xs">
              LOG: Ash executed analysis on Core.Forge
            </pre>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default AgentValidationPanel;
