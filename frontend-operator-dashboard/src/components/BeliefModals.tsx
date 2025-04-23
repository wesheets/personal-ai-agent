import React from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  useColorModeValue,
  Button,
  Icon,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  FormControl,
  FormLabel,
  Input,
  Textarea
} from '@chakra-ui/react';
import { FiEdit, FiLock, FiAlertTriangle } from 'react-icons/fi';

interface BeliefRevisionRequestProps {
  isOpen: boolean;
  onClose: () => void;
  beliefKey: string;
  currentValue: string;
  onSubmit: (beliefKey: string, newValue: string, reason: string) => void;
}

const BeliefRevisionModal: React.FC<BeliefRevisionRequestProps> = ({
  isOpen,
  onClose,
  beliefKey,
  currentValue,
  onSubmit
}) => {
  const [newValue, setNewValue] = React.useState(currentValue);
  const [reason, setReason] = React.useState('');

  const handleSubmit = () => {
    onSubmit(beliefKey, newValue, reason);
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Revise Belief: {beliefKey}</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack spacing={4}>
            <FormControl>
              <FormLabel>Current Value</FormLabel>
              <Text p={2} bg={useColorModeValue('gray.100', 'gray.700')} borderRadius="md">
                {currentValue}
              </Text>
            </FormControl>
            <FormControl isRequired>
              <FormLabel>New Value</FormLabel>
              <Textarea
                value={newValue}
                onChange={(e) => setNewValue(e.target.value)}
                placeholder="Enter new belief value"
              />
            </FormControl>
            <FormControl isRequired>
              <FormLabel>Reason for Revision</FormLabel>
              <Textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="Explain why this belief should be revised"
              />
            </FormControl>
          </VStack>
        </ModalBody>
        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            Cancel
          </Button>
          <Button 
            colorScheme="blue" 
            onClick={handleSubmit}
            isDisabled={!newValue.trim() || !reason.trim() || newValue === currentValue}
          >
            Submit Revision
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

interface BeliefReinforcementRequestProps {
  isOpen: boolean;
  onClose: () => void;
  beliefKey: string;
  currentValue: string;
  onSubmit: (beliefKey: string, reason: string) => void;
}

const BeliefReinforcementModal: React.FC<BeliefReinforcementRequestProps> = ({
  isOpen,
  onClose,
  beliefKey,
  currentValue,
  onSubmit
}) => {
  const [reason, setReason] = React.useState('');

  const handleSubmit = () => {
    onSubmit(beliefKey, reason);
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Reinforce Belief: {beliefKey}</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack spacing={4}>
            <FormControl>
              <FormLabel>Belief Value</FormLabel>
              <Text p={2} bg={useColorModeValue('gray.100', 'gray.700')} borderRadius="md">
                {currentValue}
              </Text>
            </FormControl>
            <FormControl isRequired>
              <FormLabel>Reason for Reinforcement</FormLabel>
              <Textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="Explain why this belief should be reinforced and locked"
              />
            </FormControl>
          </VStack>
        </ModalBody>
        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            Cancel
          </Button>
          <Button 
            colorScheme="green" 
            onClick={handleSubmit}
            isDisabled={!reason.trim()}
          >
            Reinforce Belief
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

interface BeliefChallengeRequestProps {
  isOpen: boolean;
  onClose: () => void;
  beliefKey: string;
  currentValue: string;
  onSubmit: (beliefKey: string, challenge: string) => void;
}

const BeliefChallengeModal: React.FC<BeliefChallengeRequestProps> = ({
  isOpen,
  onClose,
  beliefKey,
  currentValue,
  onSubmit
}) => {
  const [challenge, setChallenge] = React.useState('');

  const handleSubmit = () => {
    onSubmit(beliefKey, challenge);
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Challenge Belief: {beliefKey}</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack spacing={4}>
            <FormControl>
              <FormLabel>Belief Value</FormLabel>
              <Text p={2} bg={useColorModeValue('gray.100', 'gray.700')} borderRadius="md">
                {currentValue}
              </Text>
            </FormControl>
            <FormControl isRequired>
              <FormLabel>Challenge Statement</FormLabel>
              <Textarea
                value={challenge}
                onChange={(e) => setChallenge(e.target.value)}
                placeholder="Provide a challenge to this belief"
              />
            </FormControl>
          </VStack>
        </ModalBody>
        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            Cancel
          </Button>
          <Button 
            colorScheme="red" 
            onClick={handleSubmit}
            isDisabled={!challenge.trim()}
          >
            Submit Challenge
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export { BeliefRevisionModal, BeliefReinforcementModal, BeliefChallengeModal };
