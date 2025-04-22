import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Heading,
  Badge,
  Button,
  Flex,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Divider,
  useColorModeValue,
  Icon,
  Tooltip,
  Collapse,
  useDisclosure,
  Spinner,
  useToast
} from '@chakra-ui/react';
import { 
  FiAlertTriangle, 
  FiRefreshCw, 
  FiCpu, 
  FiFlag,
  FiArrowRight,
  FiChevronDown,
  FiChevronUp
} from 'react-icons/fi';

/**
 * LoopRepairSuggestionPanel Component
 * 
 * Renders for any loop that has:
 * - Low realism_score
 * - High drift_score
 * - Failed output or unresolved contradictions
 * 
 * Suggests:
 * - Replan
 * - Retry with different agent
 * - Flag for review
 * 
 * Includes buttons: Replan, Try with SAGE, Reflect again
 */
const LoopRepairSuggestionPanel = ({ loopId, onRepair }) => {
  const [loopData, setLoopData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [repairing, setRepairing] = useState(false);
  const { isOpen, onToggle } = useDisclosure({ defaultIsOpen: true });
  const toast = useToast();

  // Color mode values
  const bgColor = useColorModeValue('red.50', 'rgba(254, 178, 178, 0.16)');
  const borderColor = useColorModeValue('red.200', 'red.500');
  const headingColor = useColorModeValue('red.600', 'red.300');

  // Fetch loop data
  useEffect(() => {
    const fetchLoopData = async () => {
      if (!loopId) return;
      
      try {
        setLoading(true);
        const response = await fetch(`/api/loop/details/${loopId}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch loop data: ${response.status}`);
        }
        
        const data = await response.json();
        setLoopData(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching loop data:', err);
        setError(err.message);
        
        // Fallback mock data for development
        if (process.env.NODE_ENV === 'development') {
          setLoopData({
            loop_id: loopId || 'loop-123',
            title: 'Process user request for data analysis',
            status: 'failed',
            realism_score: 0.3,
            drift_score: 0.8,
            trust_score: 0.4,
            agent_id: 'ASH',
            failure_reason: 'Inconsistent output format',
            contradictions: [
              { id: 'c1', description: 'Output format does not match schema' }
            ],
            suggested_repairs: [
              { type: 'replan', confidence: 0.8, description: 'Replan with clearer output requirements' },
              { type: 'agent_switch', confidence: 0.7, agent_id: 'SAGE', description: 'Try with SAGE agent which has better schema adherence' },
              { type: 'reflect', confidence: 0.5, description: 'Additional reflection on output format requirements' }
            ]
          });
        }
      } finally {
        setLoading(false);
      }
    };
    
    fetchLoopData();
  }, [loopId]);

  // Handle repair actions
  const handleRepair = async (repairType, agentId = null) => {
    if (!loopData) return;
    
    setRepairing(true);
    
    try {
      // Prepare repair request
      const repairRequest = {
        loop_id: loopData.loop_id,
        repair_type: repairType,
        agent_id: agentId
      };
      
      // Call repair API
      const response = await fetch('/api/loop/repair', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(repairRequest)
      });
      
      if (!response.ok) {
        throw new Error(`Repair request failed: ${response.status}`);
      }
      
      const result = await response.json();
      
      // Show success toast
      toast({
        title: 'Repair initiated',
        description: `${repairType.charAt(0).toUpperCase() + repairType.slice(1)} repair for loop ${loopData.loop_id} has been initiated.`,
        status: 'success',
        duration: 5000,
        isClosable: true
      });
      
      // Call onRepair callback if provided
      if (onRepair) {
        onRepair(repairType, result);
      }
    } catch (err) {
      console.error('Error initiating repair:', err);
      
      // Show error toast
      toast({
        title: 'Repair failed',
        description: err.message,
        status: 'error',
        duration: 5000,
        isClosable: true
      });
    } finally {
      setRepairing(false);
    }
  };

  // Check if loop needs repair
  const needsRepair = (loop) => {
    if (!loop) return false;
    
    return (
      (loop.realism_score !== undefined && loop.realism_score < 0.5) ||
      (loop.drift_score !== undefined && loop.drift_score > 0.7) ||
      loop.status === 'failed' ||
      (loop.contradictions && loop.contradictions.length > 0)
    );
  };

  // Get severity level
  const getSeverityLevel = (loop) => {
    if (!loop) return 'medium';
    
    if (
      (loop.realism_score !== undefined && loop.realism_score < 0.3) ||
      (loop.drift_score !== undefined && loop.drift_score > 0.8) ||
      (loop.trust_score !== undefined && loop.trust_score < 0.3)
    ) {
      return 'high';
    }
    
    if (
      (loop.realism_score !== undefined && loop.realism_score < 0.5) ||
      (loop.drift_score !== undefined && loop.drift_score > 0.7) ||
      (loop.trust_score !== undefined && loop.trust_score < 0.5)
    ) {
      return 'medium';
    }
    
    return 'low';
  };

  // If loading, show spinner
  if (loading) {
    return (
      <Box p={4} borderWidth="1px" borderRadius="md" borderColor={borderColor} bg={bgColor}>
        <Flex justify="center" align="center" py={4}>
          <Spinner size="md" mr={3} color="red.500" />
          <Text>Analyzing loop health...</Text>
        </Flex>
      </Box>
    );
  }

  // If error, show error message
  if (error) {
    return (
      <Alert status="error" borderRadius="md">
        <AlertIcon />
        <AlertTitle mr={2}>Error analyzing loop</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  // If loop doesn't need repair, don't render anything
  if (!loopData || !needsRepair(loopData)) {
    return null;
  }

  // Get severity level
  const severity = getSeverityLevel(loopData);

  return (
    <Box 
      p={4} 
      borderWidth="2px" 
      borderRadius="md" 
      borderColor={borderColor} 
      bg={bgColor}
      mb={4}
    >
      {/* Header */}
      <Flex justify="space-between" align="center" mb={2}>
        <HStack>
          <Icon as={FiAlertTriangle} color="red.500" boxSize={5} />
          <Heading size="md" color={headingColor}>
            Loop Repair Required
          </Heading>
          <Badge 
            colorScheme={severity === 'high' ? 'red' : severity === 'medium' ? 'orange' : 'yellow'}
            variant="solid"
          >
            {severity.toUpperCase()} SEVERITY
          </Badge>
        </HStack>
        <Button 
          size="sm" 
          variant="ghost" 
          onClick={onToggle}
          rightIcon={isOpen ? <FiChevronUp /> : <FiChevronDown />}
        >
          {isOpen ? 'Hide' : 'Show'} Details
        </Button>
      </Flex>

      <Collapse in={isOpen} animateOpacity>
        <VStack align="stretch" spacing={4}>
          {/* Loop details */}
          <Box>
            <Text fontWeight="bold" mb={1}>Loop: {loopData.title || loopData.loop_id}</Text>
            <HStack spacing={2} wrap="wrap">
              <Badge colorScheme="purple">Agent: {loopData.agent_id || 'Unknown'}</Badge>
              <Badge colorScheme="red">Status: {loopData.status || 'Unknown'}</Badge>
              
              {loopData.realism_score !== undefined && (
                <Tooltip label="Realism Score - How realistic the loop's output is">
                  <Badge colorScheme={loopData.realism_score < 0.5 ? 'red' : 'green'}>
                    Realism: {(loopData.realism_score * 100).toFixed(0)}%
                  </Badge>
                </Tooltip>
              )}
              
              {loopData.drift_score !== undefined && (
                <Tooltip label="Drift Score - How far the loop has drifted from original intent">
                  <Badge colorScheme={loopData.drift_score > 0.7 ? 'red' : 'green'}>
                    Drift: {(loopData.drift_score * 100).toFixed(0)}%
                  </Badge>
                </Tooltip>
              )}
              
              {loopData.trust_score !== undefined && (
                <Tooltip label="Trust Score - Overall trustworthiness of the loop">
                  <Badge colorScheme={loopData.trust_score < 0.5 ? 'red' : 'green'}>
                    Trust: {(loopData.trust_score * 100).toFixed(0)}%
                  </Badge>
                </Tooltip>
              )}
            </HStack>
          </Box>

          {/* Failure reason */}
          {loopData.failure_reason && (
            <Alert status="error" borderRadius="md" size="sm">
              <AlertIcon />
              <Box>
                <AlertTitle>Failure Reason</AlertTitle>
                <AlertDescription>{loopData.failure_reason}</AlertDescription>
              </Box>
            </Alert>
          )}

          {/* Contradictions */}
          {loopData.contradictions && loopData.contradictions.length > 0 && (
            <Box>
              <Text fontWeight="bold" mb={2}>Unresolved Contradictions:</Text>
              <VStack align="stretch" spacing={2}>
                {loopData.contradictions.map((contradiction, index) => (
                  <Alert key={contradiction.id || index} status="warning" borderRadius="md" size="sm">
                    <AlertIcon />
                    {contradiction.description}
                  </Alert>
                ))}
              </VStack>
            </Box>
          )}

          <Divider />

          {/* Suggested repairs */}
          <Box>
            <Text fontWeight="bold" mb={2}>Suggested Repairs:</Text>
            <VStack align="stretch" spacing={3}>
              {loopData.suggested_repairs && loopData.suggested_repairs.map((repair, index) => (
                <Box 
                  key={index} 
                  p={3} 
                  borderWidth="1px" 
                  borderRadius="md" 
                  borderLeftWidth="4px"
                  borderLeftColor={
                    repair.confidence > 0.7 ? 'green.500' : 
                    repair.confidence > 0.5 ? 'yellow.500' : 
                    'red.500'
                  }
                >
                  <Flex justify="space-between" align="center" mb={1}>
                    <Text fontWeight="bold">
                      {repair.type === 'replan' ? 'Replan Loop' : 
                       repair.type === 'agent_switch' ? `Switch to ${repair.agent_id} Agent` : 
                       repair.type === 'reflect' ? 'Additional Reflection' : 
                       repair.type}
                    </Text>
                    <Badge colorScheme={
                      repair.confidence > 0.7 ? 'green' : 
                      repair.confidence > 0.5 ? 'yellow' : 
                      'red'
                    }>
                      {(repair.confidence * 100).toFixed(0)}% confidence
                    </Badge>
                  </Flex>
                  <Text fontSize="sm">{repair.description}</Text>
                </Box>
              ))}
            </VStack>
          </Box>

          <Divider />

          {/* Action buttons */}
          <Flex justify="space-between" wrap="wrap" gap={2}>
            <Button
              leftIcon={<FiRefreshCw />}
              colorScheme="blue"
              onClick={() => handleRepair('replan')}
              isLoading={repairing}
              loadingText="Initiating"
            >
              Replan
            </Button>
            
            <Button
              leftIcon={<FiCpu />}
              colorScheme="purple"
              onClick={() => handleRepair('agent_switch', 'SAGE')}
              isLoading={repairing}
              loadingText="Initiating"
            >
              Try with SAGE
            </Button>
            
            <Button
              leftIcon={<FiArrowRight />}
              colorScheme="teal"
              onClick={() => handleRepair('reflect')}
              isLoading={repairing}
              loadingText="Initiating"
            >
              Reflect Again
            </Button>
            
            <Button
              leftIcon={<FiFlag />}
              variant="outline"
              colorScheme="red"
              onClick={() => handleRepair('flag')}
              isLoading={repairing}
              loadingText="Flagging"
            >
              Flag for Review
            </Button>
          </Flex>
        </VStack>
      </Collapse>
    </Box>
  );
};

export default LoopRepairSuggestionPanel;
