import React, { useState, useEffect } from 'react';
import { 
  Box, 
  VStack, 
  Text, 
  Icon, 
  Flex, 
  Spinner, 
  useColorModeValue,
  Tooltip,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon
} from '@chakra-ui/react';
import { FaFolder, FaFolderOpen, FaFile, FaExclamationTriangle } from 'react-icons/fa';
import useFetch from '../../hooks/useFetch';

/**
 * FileTreePanel Component
 * 
 * Displays a hierarchical file tree for the current project.
 * Connected to /api/files/tree endpoint for file structure data.
 */
const FileTreePanel = ({ projectId = 'promethios-core' }) => {
  const [expandedFolders, setExpandedFolders] = useState({});
  const bgColor = useColorModeValue('white', 'gray.700');
  const hoverBgColor = useColorModeValue('gray.100', 'gray.600');
  const folderColor = useColorModeValue('blue.500', 'blue.300');
  const fileColor = useColorModeValue('gray.500', 'gray.400');
  
  // Fetch file tree data from API
  const { 
    data: fileTreeData, 
    error, 
    loading, 
    refetch 
  } = useFetch(`/api/files/tree?projectId=${projectId}`, {}, {
    refreshInterval: 60000, // Refresh every minute
    initialData: {
      schema_compliant: true,
      project_id: projectId,
      agent: 'file_system',
      files: [
        {
          name: 'app',
          type: 'folder',
          children: [
            {
              name: 'modules',
              type: 'folder',
              children: [
                { name: 'loop_metrics.py', type: 'file', size: 4502 },
                { name: 'project_lock_manager.py', type: 'file', size: 3201 },
                { name: 'snapshot_optimizer.py', type: 'file', size: 5102 }
              ]
            },
            {
              name: 'frontend',
              type: 'folder',
              children: [
                { name: 'src', type: 'folder', children: [] },
                { name: 'package.json', type: 'file', size: 1024 }
              ]
            }
          ]
        },
        {
          name: 'data',
          type: 'folder',
          children: [
            { name: 'project_manifest', type: 'folder', children: [] },
            { name: 'loop_traces', type: 'folder', children: [] }
          ]
        },
        { name: 'README.md', type: 'file', size: 2048 }
      ]
    },
    transformResponse: (data) => ({
      schema_compliant: data.schema_compliant || true,
      project_id: data.project_id || projectId,
      agent: data.agent || 'file_system',
      files: Array.isArray(data.files) ? data.files : []
    })
  });
  
  // Toggle folder expansion
  const toggleFolder = (path) => {
    setExpandedFolders(prev => ({
      ...prev,
      [path]: !prev[path]
    }));
  };
  
  // Format file size
  const formatFileSize = (size) => {
    if (size < 1024) return `${size} B`;
    if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
    return `${(size / (1024 * 1024)).toFixed(1)} MB`;
  };
  
  // Render file tree recursively
  const renderFileTree = (items, basePath = '') => {
    if (!items || !Array.isArray(items)) return null;
    
    return items.map((item, index) => {
      const currentPath = basePath ? `${basePath}/${item.name}` : item.name;
      const isExpanded = expandedFolders[currentPath];
      
      if (item.type === 'folder') {
        return (
          <Box key={index} ml={basePath ? 4 : 0}>
            <Flex 
              p={2} 
              alignItems="center" 
              cursor="pointer" 
              _hover={{ bg: hoverBgColor }}
              onClick={() => toggleFolder(currentPath)}
              borderRadius="md"
            >
              <Icon 
                as={isExpanded ? FaFolderOpen : FaFolder} 
                color={folderColor} 
                mr={2} 
              />
              <Text fontWeight="medium">{item.name}</Text>
            </Flex>
            
            {isExpanded && item.children && (
              <Box ml={4}>
                {renderFileTree(item.children, currentPath)}
              </Box>
            )}
          </Box>
        );
      } else {
        return (
          <Box key={index} ml={basePath ? 4 : 0}>
            <Flex 
              p={2} 
              alignItems="center" 
              _hover={{ bg: hoverBgColor }}
              borderRadius="md"
            >
              <Icon as={FaFile} color={fileColor} mr={2} />
              <Text>{item.name}</Text>
              {item.size && (
                <Text ml="auto" fontSize="xs" color="gray.500">
                  {formatFileSize(item.size)}
                </Text>
              )}
            </Flex>
          </Box>
        );
      }
    });
  };
  
  return (
    <Box position="relative" height="100%">
      {/* Loading indicator */}
      {loading && (
        <Box position="absolute" top="8px" right="8px">
          <Spinner size="sm" color="blue.500" />
        </Box>
      )}
      
      {/* Error indicator */}
      {error && (
        <Tooltip label={`Error: ${error}`}>
          <Box position="absolute" top="8px" right="8px">
            <Icon as={FaExclamationTriangle} color="red.500" />
          </Box>
        </Tooltip>
      )}
      
      <Text fontSize="lg" fontWeight="bold" mb={4}>
        Project Files
      </Text>
      
      {loading && !fileTreeData?.files?.length ? (
        <Flex justify="center" align="center" height="200px">
          <Spinner />
        </Flex>
      ) : error && !fileTreeData?.files?.length ? (
        <Flex 
          direction="column" 
          align="center" 
          justify="center" 
          p={6} 
          color="red.500"
        >
          <Icon as={FaExclamationTriangle} boxSize={8} mb={4} />
          <Text>Error loading file tree: {error}</Text>
        </Flex>
      ) : (
        <VStack align="stretch" spacing={0} overflowY="auto" maxHeight="calc(100vh - 200px)">
          {renderFileTree(fileTreeData?.files || [])}
        </VStack>
      )}
      
      <Text fontSize="xs" color="gray.500" mt={4}>
        Project: {fileTreeData?.project_id || projectId}
      </Text>
    </Box>
  );
};

export default FileTreePanel;
