import { Box } from '@chakra-ui/react'
import AgentChat from '../components/agent/AgentChat'

const BuilderAgentPage = () => {
  return (
    <Box pt={16} px={4} maxW="1200px" mx="auto">
      <AgentChat 
        agentType="builder"
        agentTitle="Builder Agent"
        agentDescription="Assists with code generation, architecture design, and technical problem-solving."
      />
    </Box>
  )
}

export default BuilderAgentPage
