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
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Select,
  Button,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow
} from '@chakra-ui/react';
import { 
  FaChartLine, 
  FaChartBar, 
  FaChartPie, 
  FaChartArea,
  FaExclamationTriangle, 
  FaCalendarAlt,
  FaDownload,
  FaSync,
  FaClock
} from 'react-icons/fa';
import useFetch from '../../hooks/useFetch';

/**
 * MetricsVisualization Component
 * 
 * Displays system performance metrics and visualizations.
 * Connected to /api/metrics endpoint for metrics data.
 */
const MetricsVisualization = ({ projectId = 'promethios-core' }) => {
  const [timeRange, setTimeRange] = useState('24h');
  const [metricType, setMetricType] = useState('performance');
  
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const cardBgColor = useColorModeValue('gray.50', 'gray.800');
  
  // Fetch metrics data from API
  const { 
    data: metricsData, 
    error, 
    loading, 
    refetch 
  } = useFetch(`/api/metrics?projectId=${projectId}&timeRange=${timeRange}&type=${metricType}`, {}, {
    refreshInterval: 60000, // Refresh every minute
    initialData: {
      schema_compliant: true,
      project_id: projectId,
      agent: 'metrics_service',
      timestamp: new Date().toISOString(),
      time_range: timeRange,
      metric_type: metricType,
      performance_metrics: {
        cpu_usage: {
          current: 42,
          average: 38,
          peak: 78,
          trend: 'stable',
          history: [32, 35, 40, 38, 42, 45, 42]
        },
        memory_usage: {
          current: 3.2,
          total: 8,
          average: 3.0,
          peak: 4.5,
          trend: 'increasing',
          history: [2.8, 2.9, 3.0, 3.1, 3.2, 3.2, 3.2]
        },
        response_time: {
          current: 120,
          average: 115,
          peak: 350,
          trend: 'decreasing',
          history: [140, 135, 130, 125, 120, 118, 120]
        },
        throughput: {
          current: 245,
          average: 220,
          peak: 450,
          trend: 'increasing',
          history: [180, 195, 210, 225, 240, 242, 245]
        }
      },
      cognitive_metrics: {
        belief_updates: {
          current: 42,
          average: 38,
          trend: 'stable',
          history: [35, 36, 40, 39, 41, 40, 42]
        },
        memory_accesses: {
          current: 1250,
          average: 1100,
          trend: 'increasing',
          history: [950, 1000, 1050, 1100, 1150, 1200, 1250]
        },
        reasoning_steps: {
          current: 85,
          average: 75,
          trend: 'increasing',
          history: [65, 68, 72, 75, 78, 82, 85]
        },
        contradiction_rate: {
          current: 0.5,
          average: 0.8,
          trend: 'decreasing',
          history: [1.2, 1.0, 0.9, 0.8, 0.7, 0.6, 0.5]
        }
      },
      operational_metrics: {
        active_loops: {
          current: 3,
          average: 2.5,
          peak: 8,
          history: [2, 2, 3, 3, 2, 3, 3]
        },
        completed_tasks: {
          current: 145,
          daily_average: 130,
          total: 12450,
          history: [125, 128, 132, 135, 140, 142, 145]
        },
        error_rate: {
          current: 0.8,
          average: 1.2,
          trend: 'decreasing',
          history: [1.8, 1.6, 1.4, 1.2, 1.0, 0.9, 0.8]
        },
        uptime: {
          current: 99.98,
          average: 99.95,
          history: [99.92, 99.94, 99.95, 99.95, 99.96, 99.97, 99.98]
        }
      }
    },
    transformResponse: (data) => ({
      schema_compliant: data.schema_compliant || true,
      project_id: data.project_id || projectId,
      agent: data.agent || 'metrics_service',
      timestamp: data.timestamp || new Date().toISOString(),
      time_range: data.time_range || timeRange,
      metric_type: data.metric_type || metricType,
      performance_metrics: data.performance_metrics || {},
      cognitive_metrics: data.cognitive_metrics || {},
      operational_metrics: data.operational_metrics || {}
    })
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
  
  // Get trend icon and color
  const getTrendInfo = (trend) => {
    switch (trend) {
      case 'increasing':
        return { icon: StatArrow, type: 'increase', color: 'green' };
      case 'decreasing':
        return { icon: StatArrow, type: 'decrease', color: 'red' };
      case 'stable':
      default:
        return { icon: null, type: null, color: 'blue' };
    }
  };
  
  // Handle time range change
  const handleTimeRangeChange = (e) => {
    setTimeRange(e.target.value);
  };
  
  // Handle refresh
  const handleRefresh = () => {
    refetch();
  };
  
  // Handle export metrics
  const handleExportMetrics = () => {
    console.log('Export metrics clicked');
    // In a real implementation, this would call an API to export metrics
  };
  
  // Render a simple bar chart
  const renderBarChart = (data, maxHeight = 100) => {
    if (!data || !Array.isArray(data) || data.length === 0) return null;
    
    const max = Math.max(...data);
    
    return (
      <Flex height={`${maxHeight}px`} align="flex-end" justify="space-between" mt={2}>
        {data.map((value, index) => {
          const height = max > 0 ? (value / max) * maxHeight : 0;
          
          return (
            <Tooltip key={index} label={value}>
              <Box
                height={`${height}px`}
                width="8px"
                bg="blue.400"
                borderRadius="sm"
              />
            </Tooltip>
          );
        })}
      </Flex>
    );
  };
  
  // Render metrics cards for a specific category
  const renderMetricsCards = (metrics) => {
    if (!metrics) return null;
    
    return (
      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
        {Object.entries(metrics).map(([key, metric]) => {
          const trend = getTrendInfo(metric.trend);
          const formattedKey = key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
          
          return (
            <Box 
              key={key} 
              p={4} 
              borderRadius="md" 
              bg={cardBgColor} 
              borderWidth="1px" 
              borderColor={borderColor}
            >
              <Stat>
                <StatLabel>{formattedKey}</StatLabel>
                <StatNumber>
                  {typeof metric.current === 'number' && metric.current % 1 === 0
                    ? metric.current
                    : typeof metric.current === 'number'
                    ? metric.current.toFixed(2)
                    : metric.current}
                </StatNumber>
                <StatHelpText>
                  {trend.icon && (
                    <StatArrow type={trend.type} color={trend.color} />
                  )}
                  {metric.average && (
                    <Text as="span">
                      Avg: {typeof metric.average === 'number' && metric.average % 1 === 0
                        ? metric.average
                        : typeof metric.average === 'number'
                        ? metric.average.toFixed(2)
                        : metric.average}
                    </Text>
                  )}
                  {metric.peak && (
                    <Text as="span" ml={2}>
                      Peak: {typeof metric.peak === 'number' && metric.peak % 1 === 0
                        ? metric.peak
                        : typeof metric.peak === 'number'
                        ? metric.peak.toFixed(2)
                        : metric.peak}
                    </Text>
                  )}
                </StatHelpText>
                
                {metric.history && renderBarChart(metric.history)}
              </Stat>
            </Box>
          );
        })}
      </SimpleGrid>
    );
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
      
      <Flex 
        justify="space-between" 
        align={{ base: 'flex-start', md: 'center' }}
        direction={{ base: 'column', md: 'row' }}
        mb={4}
        gap={2}
      >
        <Text fontSize="lg" fontWeight="bold">
          System Metrics
        </Text>
        
        <Flex gap={2} align="center">
          <Select 
            value={timeRange} 
            onChange={handleTimeRangeChange}
            size="sm"
            width="auto"
            icon={<FaCalendarAlt />}
          >
            <option value="1h">Last Hour</option>
            <option value="6h">Last 6 Hours</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </Select>
          
          <HStack>
            <Button 
              size="sm" 
              leftIcon={<Icon as={FaDownload} />} 
              onClick={handleExportMetrics}
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
      </Flex>
      
      {loading && !metricsData ? (
        <Flex justify="center" align="center" height="200px">
          <Spinner />
        </Flex>
      ) : error && !metricsData ? (
        <Flex 
          direction="column" 
          align="center" 
          justify="center" 
          p={6} 
          color="red.500"
        >
          <Icon as={FaExclamationTriangle} boxSize={8} mb={4} />
          <Text>Error loading metrics data: {error}</Text>
        </Flex>
      ) : (
        <Tabs colorScheme="blue" variant="enclosed">
          <TabList>
            <Tab>
              <HStack>
                <Icon as={FaChartLine} />
                <Text>Performance</Text>
              </HStack>
            </Tab>
            <Tab>
              <HStack>
                <Icon as={FaChartBar} />
                <Text>Cognitive</Text>
              </HStack>
            </Tab>
            <Tab>
              <HStack>
                <Icon as={FaChartArea} />
                <Text>Operational</Text>
              </HStack>
            </Tab>
          </TabList>
          
          <TabPanels>
            {/* Performance Metrics Tab */}
            <TabPanel p={4}>
              {renderMetricsCards(metricsData?.performance_metrics)}
            </TabPanel>
            
            {/* Cognitive Metrics Tab */}
            <TabPanel p={4}>
              {renderMetricsCards(metricsData?.cognitive_metrics)}
            </TabPanel>
            
            {/* Operational Metrics Tab */}
            <TabPanel p={4}>
              {renderMetricsCards(metricsData?.operational_metrics)}
            </TabPanel>
          </TabPanels>
        </Tabs>
      )}
      
      <Flex justify="space-between" align="center" mt={4}>
        <Text fontSize="xs" color="gray.500">
          Project: {metricsData?.project_id || projectId}
        </Text>
        <Text fontSize="xs" color="gray.500">
          <Icon as={FaClock} mr={1} />
          Last updated: {formatTimestamp(metricsData?.timestamp || Date.now())}
        </Text>
      </Flex>
    </Box>
  );
};

export default MetricsVisualization;
