import { createContext, useContext, useState } from "react"

const AgentContext = createContext()

export function AgentProvider({ children }) {
  const [agentState, setAgentState] = useState("idle") // idle | thinking | responding
  const [agentName, setAgentName] = useState("HAL")

  return (
    <AgentContext.Provider
      value={{
        agentState,
        setAgentState,
        agentName,
        setAgentName,
      }}
    >
      {children}
    </AgentContext.Provider>
  )
}

export function useAgent() {
  return useContext(AgentContext)
}
