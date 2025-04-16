// /src/components/ControlRoom.jsx
import React, { useState } from "react";
import { Flex, Box } from "@chakra-ui/react";
import SidebarNav from "./SidebarNav";
import TopHeader from "./TopHeader";
import AgentLogThread from "./AgentLogThread";
import PromptBar from "./PromptBar";
import AgentTyping from "./AgentTyping";
import AgentError from "./AgentError";

const ControlRoom = () => {
  const [logs, setLogs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentAgent, setCurrentAgent] = useState("HAL");
  const [sessionId, setSessionId] = useState("fall-app-cycle");

  const agents = [
    { id: "HAL", name: "HAL" },
    { id: "NOVA", name: "NOVA" },
  ];

  const handlePromptSubmit = async (prompt) => {
    setIsLoading(true);
    setError(null);

    const userLog = {
      sender: "You",
      message: prompt,
      timestamp: new Date().toLocaleTimeString(),
      type: "user",
    };
    setLogs((prev) => [...prev, userLog]);

    try {
      const response = await fetch("/api/respond", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: "student-001",
          session_id: sessionId,
          prompt,
        }),
      });

      const data = await response.json();

      const agentLog = {
        sender: currentAgent,
        message: data.message || "(no response)",
        timestamp: new Date().toLocaleTimeString(),
        type: "agent",
      };

      setLogs((prev) => [...prev, agentLog]);
    } catch (err) {
      console.error("Agent error:", err);
      setError("Agent failed to respond. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleAgentSelect = (agentId) => setCurrentAgent(agentId);
  const handleNavigate = (destination) => {
    console.log("Navigate to:", destination);
    // Future route support
  };

  return (
    <Flex height="100vh" overflow="hidden">
      <SidebarNav
        agents={agents}
        currentAgent={currentAgent}
        onAgentSelect={handleAgentSelect}
        onNavigate={handleNavigate}
      />

      <Flex direction="column" flex="1" overflow="hidden">
        <TopHeader sessionId={sessionId} agentStatus={isLoading ? "thinking" : "online"} />

        <Box flex="1" overflowY="auto">
          <AgentLogThread logs={logs} isLoading={false} />
          {isLoading && <AgentTyping agentName={currentAgent} />}
          {error && <AgentError errorMessage={error} onRetry={() => handlePromptSubmit(logs.at(-1)?.message)} />}
        </Box>

        <PromptBar onSubmit={handlePromptSubmit} />
      </Flex>
    </Flex>
  );
};

export default ControlRoom;
