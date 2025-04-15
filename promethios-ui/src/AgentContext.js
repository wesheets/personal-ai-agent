import { createContext, useContext, useState } from "react";

const AgentContext = createContext();

export function AgentProvider({ children }) {
  const [selectedTool, setSelectedTool] = useState("Memory");
  const [activeAgent, setActiveAgent] = useState(null);
  const [agentLogs, setAgentLogs] = useState([]);

  return (
    <AgentContext.Provider
      value={{
        selectedTool,
        setSelectedTool,
        activeAgent,
        setActiveAgent,
        agentLogs,
        setAgentLogs,
      }}
    >
      {children}
    </AgentContext.Provider>
  );
}

export function useAgent() {
  return useContext(AgentContext);
}
