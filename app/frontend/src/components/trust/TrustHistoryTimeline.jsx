import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Flex,
  Heading,
  Text,
  Badge,
  Button,
  IconButton,
  Select,
  HStack,
  VStack,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  useColorModeValue,
  Tooltip,
  Divider,
  Collapse,
  Alert,
  AlertIcon,
} from '@chakra-ui/react';
import {
  FiChevronDown,
  FiChevronUp,
  FiRefreshCw,
  FiInfo,
  FiAlertTriangle,
  FiTrendingUp,
  FiTrendingDown,
  FiMinus,
  FiFilter,
} from 'react-icons/fi';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  TimeScale,
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend,
  TimeScale
);

/**
 * TrustHistoryTimeline Component
 * 
 * Graph/visual table showing trust score changes per agent over time.
 * Annotates trust spikes, declines after contradiction, confidence decay due to drift,
 * and agent promotions/demotions.
 */
const TrustHistoryTimeline = ({
  trustHistory = {},
  agents = ['SAGE', 'HAL', 'NOVA', 'CRITIC'],
  onRefresh = () => {},
  isLoading = false,
}) => {
  // Color mode values
  const bgColor = useColorModeValue('white', 'gray.800');
  const headerBgColor = useColorModeValue('gray.50', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const hoverBgColor = useColorModeValue('gray.50', 'gray.700');
  
  // Chart colors
  const chartColors = {
    SAGE: 'rgba(66, 153, 225, 0.8)',
    HAL: 'rgba(237, 100, 166, 0.8)',
    NOVA: 'rgba(72, 187, 120, 0.8)',
    CRITIC: 'rgba(214, 158, 46, 0.8)',
  };
  
  // State for display
  const [selectedAgent, setSelectedAgent] = useState('all');
  const [timeRange, setTimeRange] = useState('week');
  const [activeTab, setActiveTab] = useState(0);
  const [expandedRows, setExpandedRows] = useState({});
  const [showFilters, setShowFilters] = useState(false);
  
  // Toggle row expansion
  const toggleRowExpansion = (id) => {
    setExpandedRows(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };
  
  // Format timestamp
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };
  
  // Format trust score
  const formatTrustScore = (score) => {
    return (score * 100).toFixed(0) + '%';
  };
  
  // Format trust delta
  const formatTrustDelta = (delta) => {
    if (Math.abs(delta) < 0.01) {
      return '0%';
    }
    
    const formattedDelta = (delta * 100).toFixed(1) + '%';
    return delta > 0 ? `+${formattedDelta}` : formattedDelta;
  };
  
  // Get trust delta icon
  const getTrustDeltaIcon = (delta) => {
    if (delta > 0.01) {
      return <FiTrendingUp color="green" />;
    } else if (delta < -0.01) {
      return <FiTrendingDown color="red" />;
    } else {
      return <FiMinus color="gray" />;
    }
  };
  
  // Get badge color based on trust score
  const getTrustScoreBadgeProps = (score) => {
    if (score >= 0.8) {
      return { colorScheme: 'green', variant: 'subtle' };
    } else if (score >= 0.6) {
      return { colorScheme: 'blue', variant: 'subtle' };
    } else if (score >= 0.4) {
      return { colorScheme: 'yellow', variant: 'subtle' };
    } else {
      return { colorScheme: 'red', variant: 'subtle' };
    }
  };
  
  // Get badge color based on status
  const getStatusBadgeProps = (status) => {
    switch (status) {
      case 'active':
        return { colorScheme: 'green', variant: 'subtle' };
      case 'warning':
        return { colorScheme: 'yellow', variant: 'subtle' };
      case 'demoted':
        return { colorScheme: 'red', variant: 'subtle' };
      case 're-evaluating':
        return { colorScheme: 'purple', variant: 'subtle' };
      default:
        return { colorScheme: 'gray', variant: 'subtle' };
    }
  };
  
  // Filter trust history based on selected agent and time range
  const filteredTrustHistory = useCallback(() => {
    let filtered = {};
    
    // Filter by agent
    if (selectedAgent === 'all') {
      filtered = { ...trustHistory };
    } else {
      filtered = {
        [selectedAgent]: trustHistory[selectedAgent] || []
      };
    }
    
    // Filter by time range
    const now = new Date();
    let timeLimit;
    
    switch (timeRange) {
      case 'day':
        timeLimit = new Date(now.setDate(now.getDate() - 1));
        break;
      case 'week':
        timeLimit = new Date(now.setDate(now.getDate() - 7));
        break;
      case 'month':
        timeLimit = new Date(now.setMonth(now.getMonth() - 1));
        break;
      case 'all':
      default:
        timeLimit = new Date(0); // Beginning of time
        break;
    }
    
    // Apply time filter
    Object.keys(filtered).forEach(agent => {
      filtered[agent] = (filtered[agent] || []).filter(event => 
        new Date(event.timestamp) >= timeLimit
      );
    });
    
    return filtered;
  }, [trustHistory, selectedAgent, timeRange]);
  
  // Get all trust events as a flat array
  const allTrustEvents = useCallback(() => {
    const filtered = filteredTrustHistory();
    let events = [];
    
    Object.keys(filtered).forEach(agent => {
      events = [...events, ...(filtered[agent] || [])];
    });
    
    // Sort by timestamp (newest first)
    return events.sort((a, b) => 
      new Date(b.timestamp) - new Date(a.timestamp)
    );
  }, [filteredTrustHistory]);
  
  // Prepare chart data
  const prepareChartData = useCallback(() => {
    const filtered = filteredTrustHistory();
    const datasets = [];
    
    // Create a dataset for each agent
    Object.keys(filtered).forEach(agent => {
      if (filtered[agent] && filtered[agent].length > 0) {
        // Sort by timestamp (oldest first for chart)
        const sortedEvents = [...filtered[agent]].sort((a, b) => 
          new Date(a.timestamp) - new Date(b.timestamp)
        );
        
        datasets.push({
          label: agent,
          data: sortedEvents.map(event => ({
            x: new Date(event.timestamp),
            y: event.trust_score
          })),
          borderColor: chartColors[agent] || `rgba(${Math.random() * 255}, ${Math.random() * 255}, ${Math.random() * 255}, 0.8)`,
          backgroundColor: chartColors[agent] || `rgba(${Math.random() * 255}, ${Math.random() * 255}, ${Math.random() * 255}, 0.8)`,
          tension: 0.1,
          pointRadius: 3,
          pointHoverRadius: 5,
        });
      }
    });
    
    return {
      datasets
    };
  }, [filteredTrustHistory, chartColors]);
  
  // Chart options
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        type: 'time',
        time: {
          unit: timeRange === 'day' ? 'hour' : timeRange === 'week' ? 'day' : 'week',
          tooltipFormat: 'MMM d, yyyy HH:mm',
          displayFormats: {
            hour: 'HH:mm',
            day: 'MMM d',
            week: 'MMM d',
          }
        },
        title: {
          display: true,
          text: 'Time'
        }
      },
      y: {
        min: 0,
        max: 1,
        title: {
          display: true,
          text: 'Trust Score'
        },
        ticks: {
          callback: function(value) {
            return (value * 100) + '%';
          }
        }
      }
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: function(context) {
            const label = context.dataset.label || '';
            const value = context.parsed.y;
            return `${label}: ${(value * 100).toFixed(1)}%`;
          }
        }
      },
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Agent Trust Score Timeline',
      },
    },
  };
  
  // Render trust history table
  const renderTrustHistoryTable = () => {
    const events = allTrustEvents();
    
    return (
      <Table variant="simple" size="sm">
        <Thead>
          <Tr>
            <Th width="40px"></Th>
            <Th>Agent</Th>
            <Th>Trust Score</Th>
            <Th>Change</Th>
            <Th>Status</Th>
            <Th>Timestamp</Th>
          </Tr>
        </Thead>
        <Tbody>
          {events.length > 0 ? (
            events.map((event) => (
              <React.Fragment key={event.id}>
                <Tr 
                  _hover={{ bg: hoverBgColor }}
                  cursor="pointer"
                  onClick={() => toggleRowExpansion(event.id)}
                >
                  <Td>
                    <IconButton
                      icon={expandedRows[event.id] ? <FiChevronUp /> : <FiChevronDown />}
                      variant="ghost"
                      size="sm"
                      aria-label={expandedRows[event.id] ? "Collapse" : "Expand"}
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleRowExpansion(event.id);
                      }}
                    />
                  </Td>
                  <Td>
                    <Badge>{event.agent}</Badge>
                  </Td>
                  <Td>
                    <Badge {...getTrustScoreBadgeProps(event.trust_score)}>
                      {formatTrustScore(event.trust_score)}
                    </Badge>
                  </Td>
                  <Td>
                    <Flex align="center">
                      {getTrustDeltaIcon(event.delta)}
                      <Text ml={1} fontSize="sm">
                        {formatTrustDelta(event.delta)}
                      </Text>
                    </Flex>
                  </Td>
                  <Td>
                    <Badge {...getStatusBadgeProps(event.status)}>
                      {event.status}
                    </Badge>
                  </Td>
                  <Td>{formatTimestamp(event.timestamp)}</Td>
                </Tr>
                
                {/* Expanded Row */}
                <Tr>
                  <Td colSpan={6} p={0}>
                    <Collapse in={expandedRows[event.id]} animateOpacity>
                      <Box p={4} bg={useColorModeValue('gray.50', 'gray.700')}>
                        <VStack align="stretch" spacing={3}>
                          <Box>
                            <Text fontWeight="bold" fontSize="sm">Loop ID:</Text>
                            <Text fontSize="sm" fontFamily="mono">
                              {event.loop_id}
                            </Text>
                          </Box>
                          
                          <Box>
                            <Text fontWeight="bold" fontSize="sm">Reason:</Text>
                            <Text fontSize="sm">
                              {event.reason}
                            </Text>
                          </Box>
                          
                          {event.metrics && (
                            <>
                              <Divider />
                              <Text fontWeight="bold" fontSize="sm">Performance Metrics:</Text>
                              <HStack spacing={4} wrap="wrap">
                                {Object.entries(event.metrics).map(([key, value]) => (
                                  <Box key={key}>
                                    <Text fontSize="xs" color="gray.500">{key.replace('_', ' ')}:</Text>
                                    <Text fontSize="sm">{typeof value === 'number' ? (value * 100).toFixed(0) + '%' : value}</Text>
                                  </Box>
                                ))}
                              </HStack>
                            </>
                          )}
                          
                          {event.status === 'demoted' && (
                            <Alert status="warning" size="sm" borderRadius="md">
                              <AlertIcon />
                              <Text fontSize="sm">
                                Agent was demoted due to low trust score.
                              </Text>
                            </Alert>
                          )}
                        </VStack>
                      </Box>
                    </Collapse>
                  </Td>
                </Tr>
              </React.Fragment>
            ))
          ) : (
            <Tr>
              <Td colSpan={6} textAlign="center" py={4}>
                {isLoading ? (
                  <Text>Loading trust history...</Text>
                ) : (
                  <Text>No trust history found</Text>
                )}
              </Td>
            </Tr>
          )}
        </Tbody>
      </Table>
    );
  };
  
  return (
    <Box
      bg={bgColor}
      borderWidth="1px"
      borderRadius="lg"
      borderColor={borderColor}
      overflow="hidden"
      boxShadow="sm"
    >
      {/* Header */}
      <Box bg={headerBgColor} px={6} py={4}>
        <Flex justify="space-between" align="center">
          <Heading size="md">Trust History Timeline</Heading>
          <HStack>
            <Button
              leftIcon={<FiFilter />}
              size="sm"
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
            >
              Filters
            </Button>
            <Button
              leftIcon={<FiRefreshCw />}
              size="sm"
              variant="outline"
              onClick={onRefresh}
              isLoading={isLoading}
            >
              Refresh
            </Button>
          </HStack>
        </Flex>
      </Box>
      
      {/* Filters */}
      <Collapse in={showFilters} animateOpacity>
        <Box p={4} borderBottomWidth="1px" borderColor={borderColor}>
          <Flex direction={{ base: 'column', md: 'row' }} gap={4}>
            <Select
              placeholder="Select agent"
              value={selectedAgent}
              onChange={(e) => setSelectedAgent(e.target.value)}
              size="sm"
            >
              <option value="all">All Agents</option>
              {agents.map(agent => (
                <option key={agent} value={agent}>{agent}</option>
              ))}
            </Select>
            
            <Select
              placeholder="Select time range"
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              size="sm"
            >
              <option value="day">Last 24 Hours</option>
              <option value="week">Last 7 Days</option>
              <option value="month">Last 30 Days</option>
              <option value="all">All Time</option>
            </Select>
          </Flex>
        </Box>
      </Collapse>
      
      {/* Tabs for Chart vs Table */}
      <Tabs variant="enclosed" onChange={setActiveTab} index={activeTab}>
        <TabList>
          <Tab>Chart View</Tab>
          <Tab>Table View</Tab>
        </TabList>
        
        <TabPanels>
          {/* Chart View */}
          <TabPanel p={4}>
            <Box height="400px">
              <Line data={prepareChartData()} options={chartOptions} />
            </Box>
            
            {/* Legend for chart events */}
            <Box mt={4}>
              <Heading size="sm" mb={2}>Event Legend</Heading>
              <Flex wrap="wrap" gap={4}>
                <HStack>
                  <Badge colorScheme="red">Trust Drop</Badge>
                  <Text fontSize="sm">Significant decrease in trust</Text>
                </HStack>
                <HStack>
                  <Badge colorScheme="green">Trust Gain</Badge>
                  <Text fontSize="sm">Significant increase in trust</Text>
                </HStack>
                <HStack>
                  <Badge colorScheme="purple">Demotion</Badge>
                  <Text fontSize="sm">Agent demoted due to low trust</Text>
                </HStack>
                <HStack>
                  <Badge colorScheme="blue">Promotion</Badge>
                  <Text fontSize="sm">Agent promoted after trust recovery</Text>
                </HStack>
              </Flex>
            </Box>
          </TabPanel>
          
          {/* Table View */}
          <TabPanel p={0}>
            {renderTrustHistoryTable()}
          </TabPanel>
        </TabPanels>
      </Tabs>
      
      {/* Trust Score Explanation */}
      <Box p={4} borderTopWidth="1px" borderColor={borderColor}>
        <Flex align="center" mb={2}>
          <FiInfo />
          <Heading size="sm" ml={2}>About Trust Scores</Heading>
        </Flex>
        <Text fontSize="sm">
          Trust scores evaluate agent performance based on summary realism, loop success, 
          reflection clarity, contradiction frequency, revision rate, and operator overrides.
          Scores decay gradually over time and are affected by agent behavior.
        </Text>
      </Box>
    </Box>
  );
};

export default TrustHistoryTimeline;
