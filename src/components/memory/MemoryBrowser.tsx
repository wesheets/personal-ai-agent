import { useState } from 'react';
import {
  Box,
  Heading,
  Text,
  Input,
  Button,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  Flex,
  InputGroup,
  InputLeftElement,
  Spinner,
  useColorModeValue,
  Tag,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  useToast
} from '@chakra-ui/react';
import { SearchIcon } from '@chakra-ui/icons';

// Mock memory item type
interface MemoryItem {
  id: string;
  content: string;
  metadata: Record<string, any>;
  similarity?: number;
  priority: boolean;
  created_at: string;
}

// Mock API function for testing
const mockSearchMemory = async () => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Return mock data
  return {
    results: [
      {
        id: '1',
        content: 'Information about React component architecture',
        metadata: { tags: ['react', 'frontend', 'architecture'], source: 'builder-agent' },
        similarity: 0.92,
        priority: true,
        created_at: '2025-03-29T14:30:00Z'
      },
      {
        id: '2',
        content: 'Docker deployment best practices for Node.js applications',
        metadata: { tags: ['docker', 'deployment', 'nodejs'], source: 'ops-agent' },
        similarity: 0.85,
        priority: false,
        created_at: '2025-03-28T10:15:00Z'
      },
      {
        id: '3',
        content: 'Research on AI agent frameworks and their capabilities',
        metadata: { tags: ['ai', 'agent', 'research'], source: 'research-agent' },
        similarity: 0.78,
        priority: true,
        created_at: '2025-03-27T16:45:00Z'
      }
    ],
    metadata: {
      total_results: 3,
      query_time_ms: 120
    }
  };
};

const MemoryBrowser = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedMemory, setSelectedMemory] = useState<MemoryItem | null>(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setIsLoading(true);
    
    try {
      // Call mock API function
      const response = await mockSearchMemory();
      
      // Update memories state with search results
      setMemories(response.results);
    } catch (error) {
      console.error('Error searching memories:', error);
      toast({
        title: 'Error',
        description: 'Failed to search memories. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      
      // Clear memories on error
      setMemories([]);
    } finally {
      setIsLoading(false);
    }
  };
  
  const viewMemoryDetails = (memory: MemoryItem) => {
    setSelectedMemory(memory);
    onOpen();
  };

  return (
    <Box>
      <Heading as="h1" size="xl" mb={2}>
        Memory Browser
      </Heading>
      <Text fontSize="md" color="gray.600" _dark={{ color: 'gray.400' }} mb={6}>
        Search and explore your personal knowledge base
      </Text>
      
      <Box
        borderWidth="1px"
        borderRadius="lg"
        overflow="hidden"
        bg={bgColor}
        borderColor={borderColor}
        p={5}
        mb={6}
      >
        <Flex>
          <InputGroup size="md" mr={4}>
            <InputLeftElement pointerEvents="none">
              <SearchIcon color="gray.400" />
            </InputLeftElement>
            <Input
              placeholder="Search memories..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleSearch();
                }
              }}
            />
          </InputGroup>
          <Button
            colorScheme="brand"
            onClick={handleSearch}
            isLoading={isLoading}
          >
            Search
          </Button>
        </Flex>
      </Box>
      
      <Box
        borderWidth="1px"
        borderRadius="lg"
        overflow="hidden"
        bg={bgColor}
        borderColor={borderColor}
      >
        {isLoading ? (
          <Flex justify="center" align="center" p={10}>
            <Spinner size="xl" color="brand.500" />
          </Flex>
        ) : memories.length === 0 ? (
          <Box p={10} textAlign="center" color="gray.500">
            <Text>No memories found. Try searching for something.</Text>
          </Box>
        ) : (
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Content</Th>
                <Th>Tags</Th>
                <Th>Source</Th>
                <Th>Relevance</Th>
                <Th>Date</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {memories.map((memory) => (
                <Tr key={memory.id}>
                  <Td maxW="300px" isTruncated>
                    {memory.priority && (
                      <Badge colorScheme="red" mr={2}>Priority</Badge>
                    )}
                    {memory.content}
                  </Td>
                  <Td>
                    <Flex wrap="wrap" gap={1}>
                      {memory.metadata.tags && memory.metadata.tags.map((tag: string) => (
                        <Tag size="sm" key={tag} colorScheme="blue">
                          {tag}
                        </Tag>
                      ))}
                    </Flex>
                  </Td>
                  <Td>{memory.metadata.source || 'Unknown'}</Td>
                  <Td>{memory.similarity ? `${(memory.similarity * 100).toFixed(0)}%` : 'N/A'}</Td>
                  <Td>{new Date(memory.created_at).toLocaleDateString()}</Td>
                  <Td>
                    <Button size="sm" onClick={() => viewMemoryDetails(memory)}>
                      View
                    </Button>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        )}
      </Box>
      
      {/* Memory Details Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Memory Details</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {selectedMemory && (
              <Box>
                <Flex mb={4}>
                  {selectedMemory.priority && (
                    <Badge colorScheme="red" mr={2}>Priority</Badge>
                  )}
                  <Text fontWeight="bold">ID: {selectedMemory.id}</Text>
                </Flex>
                
                <Box mb={4} p={4} borderWidth="1px" borderRadius="md">
                  <Text>{selectedMemory.content}</Text>
                </Box>
                
                <Box mb={4}>
                  <Text fontWeight="bold" mb={1}>Metadata:</Text>
                  <Box p={2} bg="gray.50" _dark={{ bg: 'gray.700' }} borderRadius="md">
                    <pre>{JSON.stringify(selectedMemory.metadata, null, 2)}</pre>
                  </Box>
                </Box>
                
                <Flex justify="space-between">
                  <Text>Created: {new Date(selectedMemory.created_at).toLocaleString()}</Text>
                  {selectedMemory.similarity && (
                    <Text>Relevance: {(selectedMemory.similarity * 100).toFixed(0)}%</Text>
                  )}
                </Flex>
              </Box>
            )}
          </ModalBody>
          <ModalFooter>
            <Button colorScheme="blue" mr={3} onClick={onClose}>
              Close
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default MemoryBrowser;
