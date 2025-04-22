import React, { useState, useEffect } from 'react';
import { 
  Box, 
  VStack, 
  HStack, 
  Text, 
  Icon, 
  Flex, 
  Spinner, 
  useColorModeValue,
  Tooltip,
  Badge,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Input,
  InputGroup,
  InputLeftElement,
  Select,
  Button,
  Divider
} from '@chakra-ui/react';
import { 
  FaScroll, 
  FaExclamationTriangle, 
  FaSearch, 
  FaFilter,
  FaUser,
  FaClock,
  FaTag,
  FaInfoCircle,
  FaExclamationCircle,
  FaCheckCircle,
  FaDownload,
  FaSync
} from 'react-icons/fa';
import useFetch from '../../hooks/useFetch';

/**
 * AuditLogViewer Component
 * 
 * Displays system audit logs with filtering and search capabilities.
 * Connected to /api/audit/logs endpoint for audit log data.
 */
const AuditLogViewer = ({ projectId = 'promethios-core' }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [logTypeFilter, setLogTypeFilter] = useState('all');
  const [severityFilter, setSeverityFilter] = useState('all');
  
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const cardBgColor = useColorModeValue('gray.50', 'gray.800');
  const tableHeaderBgColor = useColorModeValue('gray.50', 'gray.600');
  
  // Fetch audit log data from API
  const { 
    data: logData, 
    error, 
    loading, 
    refetch 
  } = useFetch(`/api/audit/logs?projectId=${projectId}`, {}, {
    refreshInterval: 60000, // Refresh every minute
    initialData: {
      schema_compliant: true,
      project_id: projectId,
      agent: 'auditor',
      logs: [
        {
          id: 'log-20250422-0042',
          timestamp: new Date(Date.now() - 300000).toISOString(), // 5 minutes ago
          type: 'system',
          severity: 'info',
          message: 'Memory optimization completed successfully',
          actor: 'system',
          details: 'Optimized 1,245 memory entries, reduced storage by 15%'
        },
        {
          id: 'log-20250422-0041',
          timestamp: new Date(Date.now() - 900000).toISOString(), // 15 minutes ago
          type: 'security',
          severity: 'warning',
          message: 'Unusual access pattern detected',
          actor: 'operator',
          details: 'Multiple rapid memory access requests from operator console'
        },
        {
          id: 'log-20250422-0040',
          timestamp: new Date(Date.now() - 1800000).toISOString(), // 30 minutes ago
          type: 'cognitive',
          severity: 'error',
          message: 'Belief contradiction detected',
          actor: 'belief_system',
          details: 'Contradiction between core beliefs about project goals and execution strategy'
        },
        {
          id: 'log-20250422-0039',
          timestamp: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
          type: 'operation',
          severity: 'info',
          message: 'Agent execution completed',
          actor: 'agent_runner',
          details: 'Agent "rebuilder" completed execution in 2.3 seconds'
        },
        {
          id: 'log-20250422-0038',
          timestamp: new Date(Date.now() - 7200000).toISOString(), // 2 hours ago
          type: 'system',
          severity: 'critical',
          message: 'System resource constraint',
          actor: 'system_monitor',
          details: 'Memory usage exceeded 90% threshold, initiated emergency cleanup'
        }
      ],
      pagination: {
        total: 1245,
        page: 1,
        per_page: 50,
        total_pages: 25
      }
    },
    transformResponse: (data) => ({
      schema_compliant: data.schema_compliant || true,
      project_id: data.project_id || projectId,
      agent: data.agent || 'auditor',
      logs: Array.isArray(data.logs) ? data.logs : [],
      pagination: data.pagination || { total: 0, page: 1, per_page: 50, total_pages: 1 }
    })
  });
  
  // Filter logs based on search term and filters
  const filteredLogs = logData?.logs?.filter(log => {
    // Apply search term filter
    const searchMatch = searchTerm === '' || 
      log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.details?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.actor.toLowerCase().includes(searchTerm.toLowerCase());
    
    // Apply log type filter
    const typeMatch = logTypeFilter === 'all' || log.type === logTypeFilter;
    
    // Apply severity filter
    const severityMatch = severityFilter === 'all' || log.severity === severityFilter;
    
    return searchMatch && typeMatch && severityMatch;
  });
  
  // Format timestamp
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Unknown';
    
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch (error) {
      return 'Invalid date';
    }
  };
  
  // Get severity icon and color
  const getSeverityInfo = (severity) => {
    switch (severity) {
      case 'critical':
        return { icon: FaExclamationCircle, color: 'red' };
      case 'error':
        return { icon: FaExclamationTriangle, color: 'orange' };
      case 'warning':
        return { icon: FaExclamationTriangle, color: 'yellow' };
      case 'info':
        return { icon: FaInfoCircle, color: 'blue' };
      case 'debug':
        return { icon: FaInfoCircle, color: 'gray' };
      default:
        return { icon: FaInfoCircle, color: 'gray' };
    }
  };
  
  // Handle search input change
  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };
  
  // Handle log type filter change
  const handleLogTypeChange = (e) => {
    setLogTypeFilter(e.target.value);
  };
  
  // Handle severity filter change
  const handleSeverityChange = (e) => {
    setSeverityFilter(e.target.value);
  };
  
  // Handle refresh
  const handleRefresh = () => {
    refetch();
  };
  
  // Handle export logs
  const handleExportLogs = () => {
    console.log('Export logs clicked');
    // In a real implementation, this would call an API to export logs
  };
  
  return (
    <Box position="relative">
      {/* Loading indicator */}
      {loading && (
        <Box position="absolute" top="8px" right="8px" zIndex={1}>
          <Spinner size="sm" color="blue.500" />
        </Box>
      )}
      
      {/* Error indicator */}
      {error && (
        <Tooltip label={`Error: ${error}`}>
          <Box position="absolute" top="8px" right="8px" zIndex={1}>
            <Icon as={FaExclamationTriangle} color="red.500" />
          </Box>
        </Tooltip>
      )}
      
      <Flex justify="space-between" align="center" mb={4}>
        <Text fontSize="lg" fontWeight="bold">
          Audit Logs
        </Text>
        <HStack>
          <Button 
            size="sm" 
            leftIcon={<Icon as={FaDownload} />} 
            onClick={handleExportLogs}
          >
            Export
          </Button>
          <Button 
            size="sm" 
            leftIcon={<Icon as={FaSync} />} 
            onClick={handleRefresh}
            isLoading={loading}
          >
            Refresh
          </Button>
        </HStack>
      </Flex>
      
      {loading && !logData ? (
        <Flex justify="center" align="center" height="200px">
          <Spinner />
        </Flex>
      ) : error && !logData ? (
        <Flex 
          direction="column" 
          align="center" 
          justify="center" 
          p={6} 
          color="red.500"
        >
          <Icon as={FaExclamationTriangle} boxSize={8} mb={4} />
          <Text>Error loading audit logs: {error}</Text>
        </Flex>
      ) : (
        <VStack spacing={4} align="stretch">
          {/* Filters Section */}
          <Box 
            p={4} 
            borderRadius="md" 
            bg={cardBgColor} 
            borderWidth="1px" 
            borderColor={borderColor}
          >
            <Flex 
              direction={{ base: 'column', md: 'row' }} 
              justify="space-between" 
              align={{ base: 'stretch', md: 'center' }}
              gap={3}
            >
              {/* Search Input */}
              <InputGroup>
                <InputLeftElement pointerEvents="none">
                  <Icon as={FaSearch} color="gray.300" />
                </InputLeftElement>
                <Input 
                  placeholder="Search logs..." 
                  value={searchTerm} 
                  onChange={handleSearchChange}
                />
              </InputGroup>
              
              {/* Log Type Filter */}
              <Select 
                value={logTypeFilter} 
                onChange={handleLogTypeChange}
                maxWidth={{ base: '100%', md: '200px' }}
                icon={<FaFilter />}
              >
                <option value="all">All Types</option>
                <option value="system">System</option>
                <option value="security">Security</option>
                <option value="cognitive">Cognitive</option>
                <option value="operation">Operation</option>
              </Select>
              
              {/* Severity Filter */}
              <Select 
                value={severityFilter} 
                onChange={handleSeverityChange}
                maxWidth={{ base: '100%', md: '200px' }}
                icon={<FaFilter />}
              >
                <option value="all">All Severities</option>
                <option value="critical">Critical</option>
                <option value="error">Error</option>
                <option value="warning">Warning</option>
                <option value="info">Info</option>
                <option value="debug">Debug</option>
              </Select>
            </Flex>
          </Box>
          
          {/* Logs Table Section */}
          <Box 
            borderRadius="md" 
            borderWidth="1px" 
            borderColor={borderColor}
            overflow="hidden"
          >
            <Table variant="simple" size="sm">
              <Thead bg={tableHeaderBgColor}>
                <Tr>
                  <Th width="180px">Timestamp</Th>
                  <Th width="100px">Type</Th>
                  <Th width="80px">Severity</Th>
                  <Th>Message</Th>
                  <Th width="120px">Actor</Th>
                </Tr>
              </Thead>
              <Tbody>
                {filteredLogs?.length > 0 ? (
                  filteredLogs.map((log, index) => (
                    <Tr key={index}>
                      <Td fontSize="xs">{formatTimestamp(log.timestamp)}</Td>
                      <Td>
                        <Badge>
                          {log.type}
                        </Badge>
                      </Td>
                      <Td>
                        <Badge colorScheme={getSeverityInfo(log.severity).color}>
                          <HStack spacing={1}>
                            <Icon as={getSeverityInfo(log.severity).icon} boxSize={3} />
                            <Text>{log.severity}</Text>
                          </HStack>
                        </Badge>
                      </Td>
                      <Td>
                        <Text fontSize="sm">{log.message}</Text>
                        {log.details && (
                          <Text fontSize="xs" color="gray.500" mt={1}>
                            {log.details}
                          </Text>
                        )}
                      </Td>
                      <Td fontSize="xs">
                        <HStack>
                          <Icon as={FaUser} boxSize={3} />
                          <Text>{log.actor}</Text>
                        </HStack>
                      </Td>
                    </Tr>
                  ))
                ) : (
                  <Tr>
                    <Td colSpan={5} textAlign="center" py={4}>
                      <Text color="gray.500">No logs match the current filters</Text>
                    </Td>
                  </Tr>
                )}
              </Tbody>
            </Table>
          </Box>
          
          {/* Pagination Info */}
          <Flex justify="space-between" align="center" fontSize="sm" color="gray.500">
            <Text>
              Showing {filteredLogs?.length || 0} of {logData?.pagination?.total || 0} logs
            </Text>
            <Text>
              Page {logData?.pagination?.page || 1} of {logData?.pagination?.total_pages || 1}
            </Text>
          </Flex>
        </VStack>
      )}
      
      <Text fontSize="xs" color="gray.500" mt={4}>
        Project: {logData?.project_id || projectId}
      </Text>
    </Box>
  );
};

export default AuditLogViewer;
