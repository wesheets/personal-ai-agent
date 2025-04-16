// /src/components/SidebarNav.jsx
import React from "react";
import { Box, VStack, Text, Button, Divider } from "@chakra-ui/react";

const SidebarNav = ({ agents, currentAgent, onAgentSelect, onNavigate }) => {
  return (
    <Box
      w="260px"
      bg="gray.900"
      color="white"
      p={4}
      borderRight="1px solid #2D3748"
      height="100vh"
      overflowY="auto"
    >
      <Text fontSize="lg" fontWeight="bold" mb={4}>
        🧠 Promethios
      </Text>

      <Text fontSize="sm" mb={2} color="gray.400">
        Agents
      </Text>
      <VStack align="stretch" spacing={2}>
        {agents.map((agent) => (
          <Button
            key={agent.id}
            size="sm"
            variant={agent.id === currentAgent ? "solid" : "ghost"}
            colorScheme="green"
            justifyContent="flex-start"
            onClick={() => onAgentSelect(agent.id)}
          >
            {agent.name}
          </Button>
        ))}
      </VStack>

      <Divider my={4} />

      <Text fontSize="sm" mb={2} color="gray.400">
        Verticals
      </Text>
      <VStack align="stretch" spacing={2}>
        <Button size="sm" variant="ghost" onClick={() => onNavigate("college")}>
          🎓 College Counselor
        </Button>
        <Button size="sm" variant="ghost" onClick={() => onNavigate("writer")}>
          ✍️ AI Writer
        </Button>
        {/* Add more verticals here */}
      </VStack>

      <Divider my={4} />

      <Text fontSize="sm" mb={2} color="gray.400">
        Controls
      </Text>
      <VStack align="stretch" spacing={2}>
        <Button size="sm" variant="ghost" onClick={() => onNavigate("settings")}>
          ⚙️ Settings
        </Button>
        <Button size="sm" variant="ghost" onClick={() => onNavigate("logs")}>
          📜 Logs
        </Button>
        <Button size="sm" variant="ghost" onClick={() => onNavigate("deploy")}>
          🚀 Deploy
        </Button>
      </VStack>
    </Box>
  );
};

export default SidebarNav;
