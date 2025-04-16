import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  VStack,
  HStack,
  Card,
  CardBody,
  Text,
  Badge,
  Heading,
  Divider,
  Switch,
  IconButton,
  Tooltip,
  Code,
  useColorMode,
  Flex,
  Button,
  Collapse,
  useToast
} from '@chakra-ui/react';

/**
 * AgentDebugFeedback Component
 *
 * A component for displaying debug information and feedback for agent operations.
 * Includes logs, lifecycle events, and performance metrics.
 */
const AgentDebugFeedback = ({
  agentType = '',
  isVisible = true,
  debugLogs = [],
  lifecycleEvents = {},
  performanceMetrics = {},
  onClearLogs = () => {},
  onToggleVisibility = () => {},
  onExportLogs = null
}) => {
  const { colorMode } = useColorMode();
  const mountedRef = useRef(true);
  const toast = useToast();

  // Local state
  const [renderCount, setRenderCount] = useState(0);
  const [lastUpdated, setLastUpdated] = useState(new Date().toLocaleTimeString());
  const [isExpanded, setIsExpanded] = useState(true);
  const [logFilter, setLogFilter] = useState('all');

  // Track render count for debugging
  useEffect(() => {
    if (mountedRef.current) {
      setRenderCount((prev) => prev + 1);
      setLastUpdated(new Date().toLocaleTimeString());
    }

    // Cleanup function to track component unmounting
    return () => {
      console.log('⚠️ AgentDebugFeedback unmounting - setting mountedRef to false');
      mountedRef.current = false;
    };
  }, []);

  // Format timestamp for display
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';

    try {
      if (typeof timestamp === 'string') {
        return timestamp;
      } else if (timestamp instanceof Date) {
        return timestamp.toLocaleTimeString();
      } else {
        return 'Invalid timestamp';
      }
    } catch (error) {
      console.error('Error formatting timestamp:', error);
      return 'Error';
    }
  };

  // Calculate duration between two timestamps
  const calculateDuration = (start, end) => {
    if (!start || !end) return 'N/A';

    try {
      const startTime = start instanceof Date ? start : new Date(start);
      const endTime = end instanceof Date ? end : new Date(end);

      if (isNaN(startTime.getTime()) || isNaN(endTime.getTime())) return 'Invalid';

      const durationMs = endTime - startTime;
      return `${durationMs}ms`;
    } catch (error) {
      console.error('Error calculating duration:', error);
      return 'Error';
    }
  };

  // Filter logs based on selected filter
  const getFilteredLogs = () => {
    if (!debugLogs || !Array.isArray(debugLogs)) return [];

    if (logFilter === 'all') return debugLogs;

    return debugLogs.filter((log) => {
      const logText = log?.toLowerCase() ?? '';

      switch (logFilter) {
        case 'error':
          return logText.includes('error') || logText.includes('❌');
        case 'warning':
          return logText.includes('warning') || logText.includes('⚠️');
        case 'info':
          return logText.includes('info') || logText.includes('ℹ️');
        case 'success':
          return logText.includes('success') || logText.includes('✅');
        default:
          return true;
      }
    });
  };

  // Export logs to file
  const handleExportLogs = () => {
    try {
      // If custom export handler is provided, use it
      if (typeof onExportLogs === 'function') {
        onExportLogs(debugLogs);
        return;
      }

      // Default export implementation
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const filename = `agent-debug-logs-${agentType || 'unknown'}-${timestamp}.json`;

      const exportData = {
        agentType: agentType || 'unknown',
        timestamp: new Date().toISOString(),
        logs: debugLogs || [],
        lifecycleEvents: lifecycleEvents || {},
        performanceMetrics: performanceMetrics || {},
        renderCount
      };

      const dataStr = JSON.stringify(exportData, null, 2);
      const dataUri = `data:application/json;charset=utf-8,${encodeURIComponent(dataStr)}`;

      // Create and trigger download link
      try {
        const linkElement = document.createElement('a');
        if (linkElement) {
          linkElement.setAttribute('href', dataUri);
          linkElement.setAttribute('download', filename);
          linkElement.click();

          if (toast) {
            toast({
              title: 'Logs exported',
              description: `Debug logs exported to ${filename}`,
              status: 'success',
              duration: 3000,
              isClosable: true
            });
          }
        } else {
          console.error('Failed to create download link element');
          throw new Error('Failed to create download link element');
        }
      } catch (downloadError) {
        console.error('Error creating download:', downloadError);
        throw downloadError;
      }
    } catch (error) {
      console.error('Error exporting logs:', error);

      if (toast) {
        toast({
          title: 'Export failed',
          description: `Failed to export logs: ${error?.message ?? 'Unknown error'}`,
          status: 'error',
          duration: 5000,
          isClosable: true
        });
      }
    }
  };

  // If component is not visible, return null
  if (!isVisible) return null;

  // Get filtered logs safely
  const filteredLogs = getFilteredLogs();
  const hasLogs = Array.isArray(filteredLogs) && filteredLogs.length > 0;
  const hasAllLogs = Array.isArray(debugLogs) && debugLogs.length > 0;

  // Check if we have lifecycle events
  const hasLifecycleEvents =
    lifecycleEvents &&
    typeof lifecycleEvents === 'object' &&
    Object.keys(lifecycleEvents).length > 0;

  // Check if we have performance metrics
  const hasPerformanceMetrics =
    performanceMetrics &&
    typeof performanceMetrics === 'object' &&
    Object.keys(performanceMetrics).length > 0;

  // Check if we have API duration data
  const hasApiDuration =
    hasLifecycleEvents &&
    lifecycleEvents.apiCallStart instanceof Date &&
    lifecycleEvents.apiResponse instanceof Date;

  // Check if we have total duration data
  const hasTotalDuration =
    hasLifecycleEvents &&
    lifecycleEvents.submitClick instanceof Date &&
    lifecycleEvents.spinnerResetComplete instanceof Date;

  return (
    <Card
      mt={4}
      variant="outline"
      bg={colorMode === 'light' ? 'gray.50' : 'gray.700'}
      borderColor={colorMode === 'light' ? 'gray.200' : 'gray.600'}
      size="sm"
    >
      <CardBody p={3}>
        <VStack align="stretch" spacing={2}>
          {/* Header with controls */}
          <HStack justifyContent="space-between">
            <HStack>
              <Heading size="sm">
                Agent Debug
                {agentType && (
                  <Badge ml={2} colorScheme="purple">
                    {agentType}
                  </Badge>
                )}
              </Heading>
              <Badge colorScheme="blue" variant="outline">
                Renders: {renderCount}
              </Badge>
            </HStack>

            <HStack>
              <Tooltip label="Export Logs">
                <Button
                  size="xs"
                  onClick={handleExportLogs}
                  variant="ghost"
                  colorScheme="blue"
                  isDisabled={!hasAllLogs}
                >
                  📥 Export
                </Button>
              </Tooltip>
              <Tooltip label={isExpanded ? 'Collapse' : 'Expand'}>
                <Button size="xs" onClick={() => setIsExpanded(!isExpanded)} variant="ghost">
                  {isExpanded ? '▲' : '▼'}
                </Button>
              </Tooltip>
              <Tooltip label="Toggle Debug Panel">
                <Switch size="sm" isChecked={isVisible} onChange={onToggleVisibility} />
              </Tooltip>
            </HStack>
          </HStack>

          <Collapse in={isExpanded} animateOpacity>
            <VStack align="stretch" spacing={3}>
              {/* Debug Logs Section */}
              <Box>
                <HStack justifyContent="space-between" mb={1}>
                  <Text fontSize="sm" fontWeight="bold">
                    Debug Logs
                  </Text>
                  <HStack>
                    <Box>
                      <select
                        value={logFilter}
                        onChange={(e) => setLogFilter(e.target.value)}
                        style={{
                          fontSize: '12px',
                          padding: '2px 4px',
                          borderRadius: '4px',
                          backgroundColor: colorMode === 'light' ? '#f5f5f5' : '#2d3748',
                          color: colorMode === 'light' ? '#1a202c' : '#e2e8f0',
                          border: `1px solid ${colorMode === 'light' ? '#e2e8f0' : '#4a5568'}`
                        }}
                      >
                        <option value="all">All Logs</option>
                        <option value="error">Errors</option>
                        <option value="warning">Warnings</option>
                        <option value="info">Info</option>
                        <option value="success">Success</option>
                      </select>
                    </Box>
                    <Button
                      size="xs"
                      onClick={onClearLogs}
                      colorScheme="red"
                      variant="outline"
                      isDisabled={!hasAllLogs}
                    >
                      Clear
                    </Button>
                  </HStack>
                </HStack>
                <Box
                  bg={colorMode === 'light' ? 'gray.100' : 'gray.800'}
                  p={2}
                  borderRadius="md"
                  maxH="150px"
                  overflowY="auto"
                >
                  {hasLogs ? (
                    filteredLogs.map((log, index) => (
                      <Text
                        key={`log-${index}`}
                        fontSize="xs"
                        fontFamily="monospace"
                        mb={1}
                        color={
                          log?.includes('❌') || log?.includes('error')
                            ? 'red.500'
                            : log?.includes('⚠️') || log?.includes('warning')
                              ? 'orange.500'
                              : log?.includes('✅') || log?.includes('success')
                                ? 'green.500'
                                : undefined
                        }
                      >
                        {log ?? ''}
                      </Text>
                    ))
                  ) : (
                    <Text fontSize="xs" fontStyle="italic" color="gray.500">
                      {hasAllLogs ? 'No logs match the current filter' : 'No logs available'}
                    </Text>
                  )}
                </Box>
              </Box>

              {/* Lifecycle Events Section */}
              <Box>
                <Text fontSize="sm" fontWeight="bold" mb={1}>
                  Lifecycle Events
                </Text>
                <Box bg={colorMode === 'light' ? 'gray.100' : 'gray.800'} p={2} borderRadius="md">
                  {hasLifecycleEvents ? (
                    <VStack align="stretch" spacing={1}>
                      {Object.entries(lifecycleEvents).map(([key, value]) => (
                        <HStack key={`lifecycle-${key}`} justifyContent="space-between">
                          <Text fontSize="xs" fontFamily="monospace">
                            {key}:
                          </Text>
                          <Text fontSize="xs" fontFamily="monospace">
                            {formatTimestamp(value)}
                          </Text>
                        </HStack>
                      ))}

                      {/* Add duration calculations if we have start and end events */}
                      {hasApiDuration && (
                        <HStack
                          justifyContent="space-between"
                          mt={1}
                          pt={1}
                          borderTopWidth="1px"
                          borderTopColor={colorMode === 'light' ? 'gray.200' : 'gray.600'}
                        >
                          <Text fontSize="xs" fontFamily="monospace" fontWeight="bold">
                            API Duration:
                          </Text>
                          <Text fontSize="xs" fontFamily="monospace" fontWeight="bold">
                            {calculateDuration(
                              lifecycleEvents.apiCallStart,
                              lifecycleEvents.apiResponse
                            )}
                          </Text>
                        </HStack>
                      )}

                      {hasTotalDuration && (
                        <HStack justifyContent="space-between">
                          <Text fontSize="xs" fontFamily="monospace" fontWeight="bold">
                            Total Duration:
                          </Text>
                          <Text fontSize="xs" fontFamily="monospace" fontWeight="bold">
                            {calculateDuration(
                              lifecycleEvents.submitClick,
                              lifecycleEvents.spinnerResetComplete
                            )}
                          </Text>
                        </HStack>
                      )}
                    </VStack>
                  ) : (
                    <Text fontSize="xs" fontStyle="italic" color="gray.500">
                      No lifecycle events recorded
                    </Text>
                  )}
                </Box>
              </Box>

              {/* Performance Metrics Section */}
              <Box>
                <Text fontSize="sm" fontWeight="bold" mb={1}>
                  Performance Metrics
                </Text>
                <Box bg={colorMode === 'light' ? 'gray.100' : 'gray.800'} p={2} borderRadius="md">
                  {hasPerformanceMetrics ? (
                    <VStack align="stretch" spacing={1}>
                      {Object.entries(performanceMetrics).map(([key, value]) => (
                        <HStack key={`metric-${key}`} justifyContent="space-between">
                          <Text fontSize="xs" fontFamily="monospace">
                            {key}:
                          </Text>
                          <Text
                            fontSize="xs"
                            fontFamily="monospace"
                            color={
                              value === 'true'
                                ? 'green.500'
                                : value === 'false'
                                  ? 'gray.500'
                                  : value === 'Error'
                                    ? 'red.500'
                                    : undefined
                            }
                          >
                            {value ?? 'N/A'}
                          </Text>
                        </HStack>
                      ))}
                    </VStack>
                  ) : (
                    <Text fontSize="xs" fontStyle="italic" color="gray.500">
                      No performance metrics available
                    </Text>
                  )}
                </Box>
              </Box>

              {/* Component Status */}
              <Flex justifyContent="space-between" fontSize="xs" color="gray.500">
                <Text>Last updated: {lastUpdated}</Text>
                <Text>Status: {mountedRef.current ? 'Mounted' : 'Unmounting'}</Text>
              </Flex>
            </VStack>
          </Collapse>
        </VStack>
      </CardBody>
    </Card>
  );
};

export default AgentDebugFeedback;
