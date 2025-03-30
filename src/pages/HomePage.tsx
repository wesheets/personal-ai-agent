import { Box, Text, Heading, SimpleGrid, Icon, useColorModeValue } from '@chakra-ui/react'
import { FaTools, FaServer, FaSearch, FaBrain } from 'react-icons/fa'
import { Link } from 'react-router-dom'

const HomePage = () => {
  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')
  
  const AgentCard = ({ 
    title, 
    description, 
    icon, 
    to 
  }: { 
    title: string; 
    description: string; 
    icon: React.ElementType; 
    to: string 
  }) => {
    return (
      <Box
        as={Link}
        to={to}
        p={5}
        shadow="md"
        borderWidth="1px"
        borderRadius="lg"
        bg={bgColor}
        borderColor={borderColor}
        _hover={{
          transform: 'translateY(-5px)',
          shadow: 'lg',
          borderColor: 'brand.500',
        }}
        transition="all 0.3s"
      >
        <Icon as={icon} w={10} h={10} color="brand.500" mb={4} />
        <Heading fontSize="xl" mb={2}>{title}</Heading>
        <Text color="gray.600" _dark={{ color: 'gray.400' }}>{description}</Text>
      </Box>
    )
  }
  
  return (
    <Box maxW="1200px" mx="auto" pt={20} px={4}>
      <Heading as="h1" size="xl" mb={2}>
        Personal AI Agent System
      </Heading>
      <Text fontSize="lg" color="gray.600" _dark={{ color: 'gray.400' }} mb={10}>
        Your intelligent assistant for various tasks
      </Text>
      
      <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={10} mb={10}>
        <AgentCard
          title="Builder Agent"
          description="Assists with code generation, architecture design, and technical problem-solving."
          icon={FaTools}
          to="/agent/builder"
        />
        <AgentCard
          title="Ops Agent"
          description="Helps with system operations, deployment, and infrastructure management."
          icon={FaServer}
          to="/agent/ops"
        />
        <AgentCard
          title="Research Agent"
          description="Gathers information, analyzes data, and provides insights on various topics."
          icon={FaSearch}
          to="/agent/research"
        />
        <AgentCard
          title="Memory Agent"
          description="Manages and retrieves information from your personal knowledge base."
          icon={FaBrain}
          to="/agent/memory"
        />
      </SimpleGrid>
      
      <Box mb={10}>
        <Heading as="h2" size="lg" mb={4}>
          Recent Activity
        </Heading>
        <Box p={5} shadow="md" borderWidth="1px" borderRadius="lg">
          <Text color="gray.500">No recent activity to display.</Text>
        </Box>
      </Box>
    </Box>
  )
}

export default HomePage
