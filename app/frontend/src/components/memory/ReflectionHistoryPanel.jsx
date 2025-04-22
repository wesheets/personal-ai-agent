import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Badge,
  Flex,
  Spinner,
  useColorModeValue,
  Button,
  IconButton,
  Divider,
  Tooltip,
  Heading,
  useToast,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Collapse,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon
} from '@chakra-ui/react';
import { 
  FiClock, 
  FiUser, 
  FiTag, 
  FiDownload,
  FiRefreshCw,
  FiInfo,
  FiCheck,
  FiX,
  FiEdit,
  FiArrowRight
} from 'react-icons/fi';
import useFetch from '../../hooks/useFetch';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import ReactDiffViewer from 'react-diff-viewer';

/**
 * ReflectionHistoryPanel Component
 * 
 * A side drawer or modal that displays all reflections tied to a given loop,
 * with diff views between original plans and final reflections.
 */
const ReflectionHistoryPanel = ({ loopId, nodeId, inDrawer = false }) => {
  const [activeTab, setActiveTab] = useState('reflections');
  const [selectedReflection, setSelectedReflection] = useState(null);
  const [showDiff, setShowDiff] = useState(false);
  
  const toast = useToast();
  
  // Color mode values
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const diffBgColor = useColorModeValue('gray.50', 'gray.600');
  const addedColor = useColorModeValue('green.500', 'green.300');
  const removedColor = useColorModeValue('red.500', 'red.300');
  
  // Fetch reflection history
  const { 
    data: reflectionHistory, 
    error: historyError, 
    loading: historyLoading,
    refetch: refetchHistory
  } = useFetch(
    `/api/loop/reflections?loop_id=${loopId}${nodeId ? `&node_id=${nodeId}` : ''}`,
    {},
    {
      immediate: true,
      refreshInterval: 0,
      initialData: null
    }
  );
  
  // Format timestamp
  const formatTimestamp = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch (error) {
      return 'Invalid date';
    }
  };
  
  // Get agent color
  const getAgentColor = (agent) => {
    switch (agent?.toUpperCase()) {
      case 'SAGE':
        return 'purple';
      case 'ORCHESTRATOR':
        return 'blue';
      case 'OPERATOR':
        return 'green';
      case 'SKEPTIC':
        return 'orange';
      default:
        return 'gray';
    }
  };
  
  // Get reflection type color
  const getReflectionTypeColor = (type) => {
    switch (type?.toLowerCase()) {
      case 'initial':
        return 'blue';
      case 'intermediate':
        return 'orange';
      case 'final':
        return 'green';
      case 'critique':
        return 'red';
      default:
        return 'gray';
    }
  };
  
  // Export reflection history as JSON
  const exportReflectionHistory = () => {
    if (!reflectionHistory) return;
    
    try {
      const dataStr = JSON.stringify(reflectionHistory, null, 2);
      const dataUri = `data:application/json;charset=utf-8,${encodeURIComponent(dataStr)}`;
      
      const exportFileDefaultName = `reflection-history-${loopId}${nodeId ? `-${nodeId}` : ''}-${new Date().toISOString().slice(0, 10)}.json`;
      
      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();
      
      toast({
        title: 'Reflection history exported',
        status: 'success',
        duration: 3000,
        isClosable: true
      });
    } catch (err) {
      console.error('Error exporting reflection history:', err);
      toast({
        title: 'Export failed',
        description: err.message,
        status: 'error',
        duration: 5000,
        isClosable: true
      });
    }
  };
  
  // Select a reflection to view details
  const selectReflection = (reflection) => {
    setSelectedReflection(reflection);
    setShowDiff(false);
  };
  
  // Toggle diff view
  const toggleDiffView = () => {
    setShowDiff(!showDiff);
  };
  
  // Mock data for development/testing
  const mockReflectionHistory = {
    loop_id: loopId || 'loop-123',
    reflections: [
      {
        id: 'reflection-1',
        node_id: nodeId || 'node-1',
        agent: 'ORCHESTRATOR',
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        type: 'initial',
        content: 'Initial plan for implementing the Memory Query Console and Reflection Trace Viewer',
        original_plan: 'We will implement a Memory Query Console that allows natural language queries and a Reflection Trace Viewer that shows the progression of loops.',
        tags: ['planning', 'implementation']
      },
      {
        id: 'reflection-2',
        node_id: nodeId || 'node-1',
        agent: 'SAGE',
        timestamp: new Date(Date.now() - 3400000).toISOString(),
        type: 'intermediate',
        content: 'The memory query system should include both natural language and schema-based filtering options to accommodate different operator preferences.',
        original_plan: 'We will implement a Memory Query Console that allows natural language queries and a Reflection Trace Viewer that shows the progression of loops.',
        tags: ['enhancement', 'user_experience']
      },
      {
        id: 'reflection-3',
        node_id: nodeId || 'node-1',
        agent: 'SKEPTIC',
        timestamp: new Date(Date.now() - 3200000).toISOString(),
        type: 'critique',
        content: 'The current approach to memory querying may not scale well with large datasets. Consider implementing pagination and optimized search algorithms.',
        original_plan: 'We will implement a Memory Query Console that allows natural language queries and a Reflection Trace Viewer that shows the progression of loops.',
        tags: ['performance', 'scalability']
      },
      {
        id: 'reflection-4',
        node_id: nodeId || 'node-1',
        agent: 'ORCHESTRATOR',
        timestamp: new Date(Date.now() - 3000000).toISOString(),
        type: 'final',
        content: 'Final implementation plan: Create a Memory Query Console with both natural language and schema-based filtering, implement pagination for large result sets, and optimize search algorithms for performance. The Reflection Trace Viewer will show loop progression with collapsible nodes and include a timeline view option.',
        original_plan: 'We will implement a Memory Query Console that allows natural language queries and a Reflection Trace Viewer that shows the progression of loops.',
        tags: ['final_plan', 'implementation']
      }
    ],
    summary: {
      total_reflections: 4,
      agents_involved: ['ORCHESTRATOR', 'SAGE', 'SKEPTIC'],
      key_changes: [
        'Added schema-based filtering',
        'Implemented pagination for scalability',
        'Added timeline view option',
        'Optimized search algorithms'
      ]
    }
  };
  
  // Use mock data if no real data is available
  const displayData = reflectionHistory || mockReflectionHistory;
  
  // Render reflection list
  const renderReflectionList = () => {
    if (!displayData || !displayData.reflections || displayData.reflections.length === 0) {
      return (
        <Box
          p={4}
          borderWidth="1px"
          borderRadius="md"
          borderColor={borderColor}
          borderStyle="dashed"
          textAlign="center"
        >
          <Text color="gray.500">No reflections found for this loop</Text>
        </Box>
      );
    }
    
    return (
      <VStack spacing={4} align="stretch">
        {displayData.reflections.map((reflection) => (
          <Box
            key={reflection.id}
            p={3}
            borderWidth="1px"
            borderRadius="md"
            borderColor={selectedReflection?.id === reflection.id ? 'blue.500' : borderColor}
            bg={selectedReflection?.id === reflection.id ? 'blue.50' : bgColor}
            _hover={{
              borderColor: 'blue.300',
              boxShadow: 'sm'
            }}
            transition="all 0.2s"
            cursor="pointer"
            onClick={() => selectReflection(reflection)}
          >
            <Flex justify="space-between" mb={2}>
              <HStack spacing={2}>
                <Badge colorScheme={getAgentColor(reflection.agent)}>
                  {reflection.agent}
                </Badge>
                
                <Badge colorScheme={getReflectionTypeColor(reflection.type)}>
                  {reflection.type}
                </Badge>
              </HStack>
              
              <Text fontSize="xs" color="gray.500">
                {formatTimestamp(reflection.timestamp)}
              </Text>
            </Flex>
            
            <Text noOfLines={2}>{reflection.content}</Text>
            
            {reflection.tags && reflection.tags.length > 0 && (
              <Flex mt={2} gap={2} wrap="wrap">
                {reflection.tags.map(tag => (
                  <Badge key={tag} variant="outline" colorScheme="green" size="sm">
                    {tag}
                  </Badge>
                ))}
              </Flex>
            )}
          </Box>
        ))}
      </VStack>
    );
  };
  
  // Render reflection details
  const renderReflectionDetails = () => {
    if (!selectedReflection) {
      return (
        <Box
          p={4}
          borderWidth="1px"
          borderRadius="md"
          borderColor={borderColor}
          borderStyle="dashed"
          textAlign="center"
        >
          <Text color="gray.500">Select a reflection to view details</Text>
        </Box>
      );
    }
    
    return (
      <Box>
        <Flex justify="space-between" align="center" mb={4}>
          <HStack spacing={2}>
            <Badge colorScheme={getAgentColor(selectedReflection.agent)}>
              {selectedReflection.agent}
            </Badge>
            
            <Badge colorScheme={getReflectionTypeColor(selectedReflection.type)}>
              {selectedReflection.type}
            </Badge>
          </HStack>
          
          <Text fontSize="sm" color="gray.500">
            {formatTimestamp(selectedReflection.timestamp)}
          </Text>
        </Flex>
        
        <Accordion allowToggle defaultIndex={[0]} mb={4}>
          <AccordionItem borderWidth="1px" borderRadius="md" borderColor={borderColor} mb={4}>
            <h2>
              <AccordionButton>
                <Box flex="1" textAlign="left" fontWeight="medium">
                  Reflection Content
                </Box>
                <AccordionIcon />
              </AccordionButton>
            </h2>
            <AccordionPanel pb={4}>
              <Box
                p={3}
                borderWidth="1px"
                borderRadius="md"
                borderColor={borderColor}
                bg={diffBgColor}
              >
                <Text whiteSpace="pre-wrap">{selectedReflection.content}</Text>
              </Box>
            </AccordionPanel>
          </AccordionItem>
          
          {selectedReflection.original_plan && (
            <AccordionItem borderWidth="1px" borderRadius="md" borderColor={borderColor}>
              <h2>
                <AccordionButton>
                  <Box flex="1" textAlign="left" fontWeight="medium">
                    Original Plan vs. Reflection
                  </Box>
                  <AccordionIcon />
                </AccordionButton>
              </h2>
              <AccordionPanel pb={4}>
                <Flex justify="space-between" align="center" mb={2}>
                  <Text fontSize="sm" fontWeight="medium">Compare Changes</Text>
                  
                  <Button
                    size="xs"
                    leftIcon={showDiff ? <FiX /> : <FiCheck />}
                    colorScheme={showDiff ? "red" : "green"}
                    variant="outline"
                    onClick={toggleDiffView}
                  >
                    {showDiff ? "Hide Diff" : "Show Diff"}
                  </Button>
                </Flex>
                
                {showDiff ? (
                  <Box borderWidth="1px" borderRadius="md" borderColor={borderColor} overflow="hidden">
                    <ReactDiffViewer
                      oldValue={selectedReflection.original_plan}
                      newValue={selectedReflection.content}
                      splitView={true}
                      disableWordDiff={false}
                      styles={{
                        variables: {
                          light: {
                            diffViewerBackground: diffBgColor,
                            diffViewerColor: 'inherit',
                            addedBackground: 'rgba(0, 255, 0, 0.1)',
                            addedColor: addedColor,
                            removedBackground: 'rgba(255, 0, 0, 0.1)',
                            removedColor: removedColor,
                          },
                          dark: {
                            diffViewerBackground: diffBgColor,
                            diffViewerColor: 'inherit',
                            addedBackground: 'rgba(0, 255, 0, 0.1)',
                            addedColor: addedColor,
                            removedBackground: 'rgba(255, 0, 0, 0.1)',
                            removedColor: removedColor,
                          }
                        }
                      }}
                    />
                  </Box>
                ) : (
                  <VStack spacing={4} align="stretch">
                    <Box>
                      <Text fontSize="sm" fontWeight="medium" mb={1}>Original Plan</Text>
                      <Box
                        p={3}
                        borderWidth="1px"
                        borderRadius="md"
                        borderColor={borderColor}
                        bg={diffBgColor}
                      >
                        <Text whiteSpace="pre-wrap">{selectedReflection.original_plan}</Text>
                      </Box>
                    </Box>
                    
                    <Flex justify="center" align="center">
                      <FiArrowRight size="24px" color="gray" />
                    </Flex>
                    
                    <Box>
                      <Text fontSize="sm" fontWeight="medium" mb={1}>Current Reflection</Text>
                      <Box
                        p={3}
                        borderWidth="1px"
                        borderRadius="md"
                        borderColor={borderColor}
                        bg={diffBgColor}
                      >
                        <Text whiteSpace="pre-wrap">{selectedReflection.content}</Text>
                      </Box>
                    </Box>
                  </VStack>
                )}
              </AccordionPanel>
            </AccordionItem>
          )}
        </Accordion>
        
        {selectedReflection.tags && selectedReflection.tags.length > 0 && (
          <Box mb={4}>
            <Text fontSize="sm" fontWeight="medium" mb={1}>Tags</Text>
            <Flex gap={2} wrap="wrap">
              {selectedReflection.tags.map(tag => (
                <Badge key={tag} colorScheme="green">
                  {tag}
                </Badge>
              ))}
            </Flex>
          </Box>
        )}
      </Box>
    );
  };
  
  // Render summary tab
  const renderSummary = () => {
    if (!displayData || !displayData.summary) {
      return (
        <Box
          p={4}
          borderWidth="1px"
          borderRadius="md"
          borderColor={borderColor}
          borderStyle="dashed"
          textAlign="center"
        >
          <Text color="gray.500">No summary available for this loop</Text>
        </Box>
      );
    }
    
    const { total_reflections, agents_involved, key_changes } = displayData.summary;
    
    return (
      <VStack spacing={4} align="stretch">
        <Box
          p={4}
          borderWidth="1px"
          borderRadius="md"
          borderColor={borderColor}
          bg={bgColor}
        >
          <Heading size="sm" mb={3}>Reflection Summary</Heading>
          
          <VStack spacing={3} align="stretch">
            <Flex justify="space-between">
              <Text fontWeight="medium">Total Reflections:</Text>
              <Badge colorScheme="blue" fontSize="md">{total_reflections}</Badge>
            </Flex>
            
            <Divider />
            
            <Box>
              <Text fontWeight="medium" mb={2}>Agents Involved:</Text>
              <Flex gap={2} wrap="wrap">
                {agents_involved.map(agent => (
                  <Badge key={agent} colorScheme={getAgentColor(agent)}>
                    {agent}
                  </Badge>
                ))}
              </Flex>
            </Box>
            
            <Divider />
            
            <Box>
              <Text fontWeight="medium" mb={2}>Key Changes:</Text>
              <VStack align="stretch" spacing={1}>
                {key_changes.map((change, index) => (
                  <Flex key={index} align="center">
                    <Box color="green.500" mr={2}>
                      <FiCheck />
                    </Box>
                    <Text>{change}</Text>
                  </Flex>
                ))}
              </VStack>
            </Box>
          </VStack>
        </Box>
        
        <Box
          p={4}
          borderWidth="1px"
          borderRadius="md"
          borderColor={borderColor}
          bg={bgColor}
        >
          <Heading size="sm" mb={3}>Reflection Timeline</Heading>
          
          <VStack spacing={0} align="stretch">
            {displayData.reflections
              .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
              .map((reflection, index) => (
                <Flex key={reflection.id} position="relative">
                  {/* Timeline connector */}
                  {index < displayData.reflections.length - 1 && (
                    <Box
                      position="absolute"
                      left="12px"
                      top="20px"
                      bottom="-12px"
                      width="2px"
                      bg="gray.300"
                    />
                  )}
                  
                  <Box
                    width="24px"
                    height="24px"
                    borderRadius="full"
                    bg={getAgentColor(reflection.agent)}
                    display="flex"
                    alignItems="center"
                    justifyContent="center"
                    color="white"
                    fontWeight="bold"
                    fontSize="xs"
                    mr={3}
                    flexShrink={0}
                    zIndex="1"
                  >
                    {index + 1}
                  </Box>
                  
                  <Box mb={4} flex="1">
                    <Flex justify="space-between" align="center" mb={1}>
                      <HStack spacing={2}>
                        <Badge colorScheme={getAgentColor(reflection.agent)}>
                          {reflection.agent}
                        </Badge>
                        
                        <Badge colorScheme={getReflectionTypeColor(reflection.type)}>
                          {reflection.type}
                        </Badge>
                      </HStack>
                      
                      <Text fontSize="xs" color="gray.500">
                        {formatTimestamp(reflection.timestamp)}
                      </Text>
                    </Flex>
                    
                    <Text fontSize="sm" noOfLines={2}>{reflection.content}</Text>
                    
                    <Button
                      size="xs"
                      variant="link"
                      mt={1}
                      onClick={() => {
                        selectReflection(reflection);
                        setActiveTab('reflections');
                      }}
                    >
                      View details
                    </Button>
                  </Box>
                </Flex>
              ))}
          </VStack>
        </Box>
      </VStack>
    );
  };
  
  return (
    <Box>
      {/* Header */}
      {!inDrawer && (
        <Flex justify="space-between" align="center" mb={4}>
          <Heading size="md">
            Reflection History {loopId ? `for Loop #${loopId}` : ''}
          </Heading>
          
          <HStack spacing={2}>
            <Tooltip label="Refresh">
              <IconButton
                icon={<FiRefreshCw />}
                size="sm"
                variant="ghost"
                aria-label="Refresh"
                onClick={refetchHistory}
                isLoading={historyLoading}
              />
            </Tooltip>
            
            <Tooltip label="Export Reflection History">
              <IconButton
                icon={<FiDownload />}
                size="sm"
                variant="ghost"
                aria-label="Export"
                onClick={exportReflectionHistory}
                isDisabled={!displayData}
              />
            </Tooltip>
          </HStack>
        </Flex>
      )}
      
      {/* Loading state */}
      {historyLoading && (
        <Flex justify="center" align="center" height="200px">
          <Spinner size="xl" />
        </Flex>
      )}
      
      {/* Error state */}
      {historyError && (
        <Box
          p={4}
          borderWidth="1px"
          borderRadius="md"
          borderColor="red.300"
          bg="red.50"
          color="red.800"
        >
          <Heading size="sm" mb={2}>Error Loading Reflection History</Heading>
          <Text>{historyError}</Text>
        </Box>
      )}
      
      {/* Reflection history content */}
      {!historyLoading && displayData && (
        <Tabs variant="enclosed" colorScheme="blue" index={activeTab === 'reflections' ? 0 : 1} onChange={(index) => setActiveTab(index === 0 ? 'reflections' : 'summary')}>
          <TabList>
            <Tab>Reflections</Tab>
            <Tab>Summary</Tab>
          </TabList>
          
          <TabPanels>
            <TabPanel p={0} pt={4}>
              <Flex direction={{ base: "column", md: "row" }} gap={4}>
                <Box flex="1" minW="0">
                  {renderReflectionList()}
                </Box>
                
                <Box flex="1" minW="0">
                  {renderReflectionDetails()}
                </Box>
              </Flex>
            </TabPanel>
            
            <TabPanel p={0} pt={4}>
              {renderSummary()}
            </TabPanel>
          </TabPanels>
        </Tabs>
      )}
    </Box>
  );
};

export default ReflectionHistoryPanel;
