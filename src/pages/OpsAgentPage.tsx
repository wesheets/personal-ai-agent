import { Box } from '@chakra-ui/react'
import AgentChat from '../components/agent/AgentChat'

const OpsAgentPage = () => {
  return (
    <Box pt={16} px={4} maxW="1200px" mx="auto">
      <AgentChat 
        agentType="ops"
        agentTitle="Ops Agent"
        agentDescription="Helps with system operations, deployment, and infrastructure management."
      />
    </Box>
  )
}

export default OpsAgentPage
