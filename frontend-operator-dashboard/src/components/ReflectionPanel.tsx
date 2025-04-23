import React from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Badge,
  useColorModeValue,
  Button,
  Icon,
  Progress
} from '@chakra-ui/react';
import { FiEdit, FiLock, FiAlertTriangle } from 'react-icons/fi';

interface Beliefs {
  purpose: string;
  role: string;
  limitations: string[];
}

interface ReinforcedBeliefs {
  [key: string]: {
    locked: boolean;
    reason: string;
    timestamp: string;
  };
}

interface BeliefRevision {
  belief_key: string;
  old_value: string;
  new_value: string;
  reason: string;
  timestamp: string;
}

interface ReflectionPanelProps {
  beliefs: Beliefs;
  belief_stability: Record<string, number>;
  reinforced_beliefs: ReinforcedBeliefs;
  revision_log: BeliefRevision[];
  volatility_flags: string[];
  onRevise: (beliefKey: string) => void;
  onReinforce: (beliefKey: string) => void;
  onChallenge: (beliefKey: string) => void;
}

const ReflectionPanel: React.FC<ReflectionPanelProps> = ({
  beliefs,
  belief_stability,
  reinforced_beliefs,
  revision_log,
  volatility_flags,
  onRevise,
  onReinforce,
  onChallenge
}) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const [showRevisionLog, setShowRevisionLog] = React.useState(false);

  // Get stability color based on value
  const getStabilityColor = (value: number) => {
    if (value < 0.3) return 'red';
    if (value < 0.7) return 'yellow';
    return 'green';
  };

  // Format timestamp
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  // Get last revised belief and reason
  const getLastRevision = () => {
    if (revision_log.length === 0) return null;
    return revision_log[revision_log.length - 1];
  };

  const lastRevision = getLastRevision();

  return (
    <Box borderWidth="1px" borderRadius="lg" borderColor={borderColor} bg={bgColor} p={4} mb={4}>
      <Text fontWeight="bold" mb={3}>
        Self-Reflection
      </Text>

      {/* Purpose, Role, Limitations */}
      <VStack align="stretch" spacing={3} mb={4}>
        <Box>
          <HStack mb={1} justify="space-between">
            <Text fontWeight="medium">Purpose</Text>
            {reinforced_beliefs['purpose'] && (
              <Badge colorScheme="green">
                <Icon as={FiLock} mr={1} />
                Locked
              </Badge>
            )}
          </HStack>
          <Text fontSize="sm" mb={2}>
            {beliefs.purpose}
          </Text>
          <HStack>
            <Text fontSize="xs" width="80px">
              Stability:
            </Text>
            <Progress
              value={belief_stability['purpose'] * 100}
              size="xs"
              colorScheme={getStabilityColor(belief_stability['purpose'])}
              width="100%"
            />
            <Text fontSize="xs" width="40px">
              {Math.round(belief_stability['purpose'] * 100)}%
            </Text>
          </HStack>
        </Box>

        <Box>
          <HStack mb={1} justify="space-between">
            <Text fontWeight="medium">Role</Text>
            {reinforced_beliefs['role'] && (
              <Badge colorScheme="green">
                <Icon as={FiLock} mr={1} />
                Locked
              </Badge>
            )}
          </HStack>
          <Text fontSize="sm" mb={2}>
            {beliefs.role}
          </Text>
          <HStack>
            <Text fontSize="xs" width="80px">
              Stability:
            </Text>
            <Progress
              value={belief_stability['role'] * 100}
              size="xs"
              colorScheme={getStabilityColor(belief_stability['role'])}
              width="100%"
            />
            <Text fontSize="xs" width="40px">
              {Math.round(belief_stability['role'] * 100)}%
            </Text>
          </HStack>
        </Box>

        <Box>
          <HStack mb={1} justify="space-between">
            <Text fontWeight="medium">Limitations</Text>
            {reinforced_beliefs['limitations'] && (
              <Badge colorScheme="green">
                <Icon as={FiLock} mr={1} />
                Locked
              </Badge>
            )}
          </HStack>
          <VStack align="stretch" spacing={1} mb={2}>
            {beliefs.limitations.map((limitation, index) => (
              <Text key={index} fontSize="sm">
                • {limitation}
              </Text>
            ))}
          </VStack>
          <HStack>
            <Text fontSize="xs" width="80px">
              Stability:
            </Text>
            <Progress
              value={belief_stability['limitations'] * 100}
              size="xs"
              colorScheme={getStabilityColor(belief_stability['limitations'])}
              width="100%"
            />
            <Text fontSize="xs" width="40px">
              {Math.round(belief_stability['limitations'] * 100)}%
            </Text>
          </HStack>
        </Box>
      </VStack>

      {/* Last revised information */}
      {lastRevision && (
        <Box
          p={2}
          borderWidth="1px"
          borderRadius="md"
          borderColor={borderColor}
          bg={useColorModeValue('gray.50', 'gray.700')}
          mb={4}
        >
          <HStack mb={1}>
            <Text fontSize="xs" fontWeight="medium">
              Last revised:
            </Text>
            <Text fontSize="xs">{lastRevision.belief_key}</Text>
            <Text fontSize="xs" color={useColorModeValue('gray.500', 'gray.400')}>
              {formatTime(lastRevision.timestamp)}
            </Text>
          </HStack>
          <Text fontSize="xs">Reason: {lastRevision.reason}</Text>
        </Box>
      )}

      {/* Volatility flags */}
      {volatility_flags.length > 0 && (
        <Box
          p={2}
          borderWidth="1px"
          borderRadius="md"
          borderColor="red.300"
          bg={useColorModeValue('red.50', 'red.900')}
          mb={4}
        >
          <HStack mb={1}>
            <Icon as={FiAlertTriangle} color="red.500" />
            <Text fontSize="sm" fontWeight="medium" color="red.500">
              Volatility Detected
            </Text>
          </HStack>
          <VStack align="stretch" spacing={1}>
            {volatility_flags.map((flag, index) => (
              <Text key={index} fontSize="xs">
                • {flag}
              </Text>
            ))}
          </VStack>
        </Box>
      )}

      {/* Revision log (collapsible) */}
      <Box mb={4}>
        <Button
          size="xs"
          variant="outline"
          onClick={() => setShowRevisionLog(!showRevisionLog)}
          mb={2}
        >
          {showRevisionLog ? 'Hide' : 'Show'} Revision History
        </Button>
        
        {showRevisionLog && revision_log.length > 0 && (
          <VStack align="stretch" spacing={2} mt={2} maxH="200px" overflowY="auto">
            {revision_log.map((revision, index) => (
              <Box
                key={index}
                p={2}
                borderWidth="1px"
                borderRadius="md"
                borderColor={borderColor}
                fontSize="xs"
              >
                <HStack mb={1} justify="space-between">
                  <Text fontWeight="medium">{revision.belief_key}</Text>
                  <Text color={useColorModeValue('gray.500', 'gray.400')}>
                    {formatTime(revision.timestamp)}
                  </Text>
                </HStack>
                <Text>From: {revision.old_value}</Text>
                <Text>To: {revision.new_value}</Text>
                <Text fontStyle="italic">Reason: {revision.reason}</Text>
              </Box>
            ))}
          </VStack>
        )}
      </Box>

      {/* Action buttons */}
      <HStack spacing={2} justify="flex-end">
        <Button
          size="sm"
          leftIcon={<Icon as={FiAlertTriangle} />}
          colorScheme="red"
          variant="outline"
          onClick={() => onChallenge('purpose')}
        >
          Challenge Belief
        </Button>
        <Button
          size="sm"
          leftIcon={<Icon as={FiEdit} />}
          colorScheme="blue"
          variant="outline"
          onClick={() => onRevise('purpose')}
          isDisabled={reinforced_beliefs['purpose']?.locked}
        >
          Revise Belief
        </Button>
        <Button
          size="sm"
          leftIcon={<Icon as={FiLock} />}
          colorScheme="green"
          onClick={() => onReinforce('purpose')}
        >
          Reinforce Belief
        </Button>
      </HStack>
    </Box>
  );
};

export default ReflectionPanel;
