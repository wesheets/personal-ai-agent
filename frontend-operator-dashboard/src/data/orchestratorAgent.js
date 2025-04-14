// Agent context system - Orchestrator definition
const orchestratorAgent = {
  id: 'orchestrator',
  name: 'Orchestrator',
  persona: 'Planner, coordinator, narrator',
  role: 'system',
  loopDepth: 0, // non-executing, planning only
  color: 'purple',
  icon: 'FiCpu',
  status: 'active',
  activeTask: 'Coordinating agent activities',
  lastMemoryEntry: 'Planning sequence for HAL onboarding',
  tools: ['plan.create', 'agent.assign', 'checkpoint.create'],
  reflection: 'Preparing to coordinate HAL onboarding sequence. Will need to establish proper checkpoints and validation steps.'
};

export default orchestratorAgent;
