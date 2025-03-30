import { Box } from '@chakra-ui/react'
import AgentChat from '../components/agent/AgentChat'

const MemoryAgentPage = () => {
  return (
    <Box pt={16} px={4} maxW="1200px" mx="auto">
      <AgentChat 
        agentType="memory"
        agentTitle="Memory Agent"
        agentDescription="Manages and retrieves information from your personal knowledge base."
      />
    </Box>
  )
}

export default MemoryAgentPage
