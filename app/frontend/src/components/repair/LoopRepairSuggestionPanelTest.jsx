import React, { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Heading,
  Button,
  Select,
  FormControl,
  FormLabel,
  useToast,
  Container,
  Divider,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Code,
  Switch,
  Badge
} from '@chakra-ui/react';
import LoopRepairSuggestionPanel from './LoopRepairSuggestionPanel';

/**
 * Test component for LoopRepairSuggestionPanel
 * 
 * This component demonstrates the LoopRepairSuggestionPanel functionality
 * with sample loop data and interaction handlers.
 */
const LoopRepairSuggestionPanelTest = () => {
  const [selectedLoopId, setSelectedLoopId] = useState('loop-123');
  const [repairResult, setRepairResult] = useState(null);
  const toast = useToast();

  // Sample loops for testing
  const sampleLoops = [
    { id: 'loop-123', name: 'Failed Data Processing Loop', status: 'failed' },
    { id: 'loop-456', name: 'High Drift Score Loop', status: 'completed' },
    { id: 'loop-789', name: 'Low Realism Score Loop', status: 'completed' },
    { id: 'loop-101', name: 'Healthy Loop (No Issues)', status: 'completed' }
  ];

  // Handle repair action
  const handleRepair = (repairType, result) => {
    setRepairResult({
      type: repairType,
      loop_id: selectedLoopId,
      timestamp: new Date().toISOString(),
      ...result
    });

    toast({
      title: 'Repair Action Triggered',
      description: `${repairType} repair initiated for loop ${selectedLoopId}`,
      status: 'success',
      duration: 3000,
      isClosable: true,
    });
  };

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={8} align="stretch">
        <Box>
          <Heading size="lg" mb={4}>Loop Repair Suggestion Panel Test</Heading>
          <Text>
            This test component demonstrates the LoopRepairSuggestionPanel functionality with sample loop data.
            You can select different loops to see how the panel renders for various loop health conditions.
          </Text>
        </Box>

        <Box p={4} borderWidth="1px" borderRadius="md">
          <FormControl mb={4}>
            <FormLabel>Select Loop</FormLabel>
            <Select
              value={selectedLoopId}
              onChange={(e) => setSelectedLoopId(e.target.value)}
            >
              {sampleLoops.map(loop => (
                <option key={loop.id} value={loop.id}>
                  {loop.name} ({loop.status})
                </option>
              ))}
            </Select>
          </FormControl>

          {repairResult && (
            <Alert status="info" mb={4}>
              <AlertIcon />
              <Box>
                <AlertTitle>Repair Action Triggered</AlertTitle>
                <AlertDescription>
                  <Text>Type: <Code>{repairResult.type}</Code></Text>
                  <Text>Loop: <Code>{repairResult.loop_id}</Code></Text>
                  <Text>Time: <Code>{new Date(repairResult.timestamp).toLocaleString()}</Code></Text>
                </AlertDescription>
              </Box>
            </Alert>
          )}

          <Button
            mb={4}
            onClick={() => setRepairResult(null)}
            isDisabled={!repairResult}
          >
            Clear Result
          </Button>
        </Box>

        <Divider />

        <Box>
          <Heading size="md" mb={4}>Loop Repair Suggestion Panel</Heading>
          <LoopRepairSuggestionPanel 
            loopId={selectedLoopId} 
            onRepair={handleRepair} 
          />
          
          {selectedLoopId === 'loop-101' && (
            <Alert status="info" mt={4}>
              <AlertIcon />
              <AlertDescription>
                This is a healthy loop with no issues, so the repair panel is not displayed.
              </AlertDescription>
            </Alert>
          )}
        </Box>

        <Box p={4} borderWidth="1px" borderRadius="md">
          <Heading size="md" mb={4}>Component Notes</Heading>
          <VStack align="start" spacing={2}>
            <Text>• The panel only renders for loops with issues (low realism score, high drift score, or failed status)</Text>
            <Text>• Different severity levels are indicated by color intensity and badges</Text>
            <Text>• The panel provides suggested repair actions based on the specific issues detected</Text>
            <Text>• Action buttons trigger the appropriate repair API calls</Text>
            <Text>• The panel can be collapsed to save space when details aren't needed</Text>
          </VStack>
        </Box>
      </VStack>
    </Container>
  );
};

export default LoopRepairSuggestionPanelTest;
