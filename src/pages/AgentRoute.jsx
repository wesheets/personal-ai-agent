import { useParams } from 'react-router-dom'
import AgentChat from '../AgentChat'

export default function AgentRoute() {
  const { agentId } = useParams()
  return <AgentChat agentId={agentId} />
}
