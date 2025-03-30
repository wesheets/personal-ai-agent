import { Box } from '@chakra-ui/react'
import AgentChat from '../components/agent/AgentChat'

const ResearchAgentPage = () => {
  return (
    <Box pt={16} px={4} maxW="1200px" mx="auto">
      <AgentChat 
        agentType="research"
        agentTitle="Research Agent"
        agentDescription="Gathers information, analyzes data, and provides insights on various topics."
      />
    </Box>
  )
}

export default ResearchAgentPage
