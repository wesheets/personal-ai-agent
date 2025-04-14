import React, { useState } from 'react';
import { 
  Box, 
  Grid, 
  GridItem, 
  useColorModeValue, 
  useDisclosure,
  IconButton,
  Drawer,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  DrawerHeader,
  DrawerBody,
  Icon
} from '@chakra-ui/react';
import { FiMenu } from 'react-icons/fi';
import { v4 as uuidv4 } from 'uuid';

import Sidebar from '../components/Sidebar';
import ThreadedChat from '../components/chat/ThreadedChat';
import AgentSandboxCard from '../components/AgentSandboxCard';
import CheckpointApprovalPanel from '../components/CheckpointApprovalPanel';
import ToolOutputCard from '../components/ToolOutputCard';
import InputUI from '../components/InputUI';
import { UIMessage, Attachment } from '../models/Message';

// Define checkpoint types
type CheckpointStatus = 'pending' | 'approved' | 'rejected';
type CheckpointType = 'hard' | 'soft';

interface Checkpoint {
  id: string;
  title: string;
  description: string;
  type: CheckpointType;
  status: CheckpointStatus;
  timestamp: Date;
}

const Dashboard: React.FC = () => {
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  
  // State for right panel visibility
  const { isOpen: isSandboxOpen, onToggle: onToggleSandbox } = useDisclosure();
  
  // State for active agent/thread
  const [activeAgent, setActiveAgent] = useState('hal');
  const [, setActiveThread] = useState('');
  
  // Initial state with mock messages for testing
  const [messages, setMessages] = useState<UIMessage[]>([
    {
      message_id: 'msg_1',
      thread_parent_id: null,
      goal_id: 'goal_1',
      agent_id: 'orchestrator',
      sender: 'agent',
      content: 'Consultation received. Analyzing requirements for the new feature.',
      timestamp: new Date(Date.now() - 3600000),
      isExpanded: false
    },
    {
      message_id: 'msg_2',
      thread_parent_id: null,
      goal_id: 'goal_1',
      agent_id: 'hal',
      sender: 'agent',
      content: 'I found several relevant articles about React state management. Would you like me to summarize the key points?',
      timestamp: new Date(Date.now() - 3000000),
      isExpanded: false
    },
    {
      message_id: 'msg_3',
      thread_parent_id: null,
      goal_id: 'goal_1',
      agent_id: 'operator',
      sender: 'operator',
      content: 'Yes, please focus on the differences between Context API and Redux.',
      timestamp: new Date(Date.now() - 2400000),
      isExpanded: true
    },
    {
      message_id: 'msg_4',
      thread_parent_id: 'msg_3',
      goal_id: 'goal_1',
      agent_id: 'hal',
      sender: 'agent',
      content: 'Here\'s a comparison of Context API and Redux:\n\n**Context API**:\n- Built into React\n- Simpler setup\n- Good for low-frequency updates\n- Less boilerplate\n- No middleware support\n\n**Redux**:\n- External library\n- More structured approach\n- Better for complex state logic\n- Developer tools\n- Middleware support',
      timestamp: new Date(Date.now() - 2000000)
    },
    {
      message_id: 'msg_5',
      thread_parent_id: 'msg_3',
      goal_id: 'goal_1',
      agent_id: 'operator',
      sender: 'operator',
      content: 'What about performance considerations?',
      timestamp: new Date(Date.now() - 1500000)
    },
    {
      message_id: 'msg_6',
      thread_parent_id: 'msg_3',
      goal_id: 'goal_1',
      agent_id: 'hal',
      sender: 'agent',
      content: 'Context API is generally better for smaller applications or when you need to share state between a few components. Redux shines in larger applications with complex state management needs.',
      timestamp: new Date(Date.now() - 1000000)
    }
  ]);

  // Mock checkpoints
  const [checkpoints, setCheckpoints] = useState<Checkpoint[]>([
    {
      id: 'checkpoint_1',
      title: 'Research Complete',
      description: 'Confirm that the research phase for React state management is complete and sufficient for implementation.',
      type: 'hard',
      status: 'pending',
      timestamp: new Date(Date.now() - 500000)
    },
    {
      id: 'checkpoint_2',
      title: 'Implementation Approach',
      description: 'Approve the proposed implementation approach using Context API for the current feature.',
      type: 'soft',
      status: 'pending',
      timestamp: new Date(Date.now() - 300000)
    }
  ]);

  // Handle sending a new message or reply
  const handleSendMessage = (content: string, threadParentId?: string) => {
    const newMessage: UIMessage = {
      message_id: uuidv4(),
      thread_parent_id: threadParentId || null,
      goal_id: 'goal_1',
      agent_id: 'operator',
      sender: 'operator',
      content,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, newMessage]);
    
    // If this is a reply, make sure the parent thread is expanded
    if (threadParentId) {
      setMessages(prev => 
        prev.map(msg => 
          msg.message_id === threadParentId 
            ? { ...msg, isExpanded: true } 
            : msg
        )
      );
    }
    
    // Auto-open sandbox panel when a new message is sent
    if (!isSandboxOpen) {
      onToggleSandbox();
    }
  };
  
  // Handle input with files
  const handleInputWithFiles = (content: string, files?: File[]) => {
    // Convert files to attachments if needed
    let attachments: Attachment[] | undefined;
    if (files && files.length > 0) {
      attachments = files.map(file => ({
        id: uuidv4(),
        type: file.type.startsWith('image/') ? 'image' : 'file',
        content: URL.createObjectURL(file),
        name: file.name,
        timestamp: new Date()
      }));
    }
    
    const newMessage: UIMessage = {
      message_id: uuidv4(),
      thread_parent_id: null,
      goal_id: 'goal_1',
      agent_id: 'operator',
      sender: 'operator',
      content,
      timestamp: new Date(),
      attachments
    };
    
    setMessages(prev => [...prev, newMessage]);
  };
  
  // Handle marking a thread as resolved
  const handleMarkResolved = (messageId: string) => {
    setMessages(prev => 
      prev.map(msg => {
        // Mark the parent message as resolved
        if (msg.message_id === messageId) {
          return { ...msg, isResolved: true };
        }
        
        // Also mark all child messages in this thread as resolved
        if (msg.thread_parent_id === messageId) {
          return { ...msg, isResolved: true };
        }
        
        return msg;
      })
    );
  };
  
  // Handle summarizing a thread
  const handleSummarizeThread = (messageId: string) => {
    // In a real implementation, this would call an API to generate a summary
    // For testing, we'll just add a system message with a mock summary
    
    const summaryMessage: UIMessage = {
      message_id: uuidv4(),
      thread_parent_id: messageId,
      goal_id: 'goal_1',
      agent_id: 'orchestrator',
      sender: 'system',
      content: `Thread Summary: This thread discusses the differences between Context API and Redux for React state management, including setup complexity, performance considerations, and use cases.`,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, summaryMessage]);
  };
  
  // Handle exporting a thread as markdown
  const handleExportMarkdown = (messageId: string) => {
    // In a real implementation, this would generate and download a markdown file
    console.log(`Exporting thread ${messageId} as markdown`);
  };
  
  // Handle exporting a thread as PDF
  const handleExportPDF = (messageId: string) => {
    // In a real implementation, this would generate and download a PDF file
    console.log(`Exporting thread ${messageId} as PDF`);
  };
  
  // Handle checkpoint actions
  const handleApproveCheckpoint = (checkpointId: string) => {
    setCheckpoints(prev => 
      prev.map(cp => 
        cp.id === checkpointId 
          ? { ...cp, status: 'approved' as CheckpointStatus } 
          : cp
      )
    );
  };
  
  const handleRejectCheckpoint = (checkpointId: string) => {
    setCheckpoints(prev => 
      prev.map(cp => 
        cp.id === checkpointId 
          ? { ...cp, status: 'rejected' as CheckpointStatus } 
          : cp
      )
    );
  };
  
  const handleCommentCheckpoint = (checkpointId: string) => {
    // In a real implementation, this would open a comment dialog
    console.log(`Adding comment to checkpoint ${checkpointId}`);
  };

  return (
    <Box p={4} bg={bgColor} minH="100vh">
      <Grid
        templateColumns={`260px 1fr ${isSandboxOpen ? '280px' : '0px'}`}
        templateRows="1fr auto"
        gap={4}
        h="calc(100vh - 32px)"
        transition="all 0.3s ease"
      >
        {/* Left Panel - Sidebar */}
        <GridItem rowSpan={2} colSpan={1} overflow="hidden">
          <Sidebar 
            activeAgent={activeAgent}
            onSelectAgent={setActiveAgent}
            onSelectThread={setActiveThread}
          />
        </GridItem>
        
        {/* Center Panel - ThreadedChat */}
        <GridItem rowSpan={1} colSpan={1} overflow="hidden" position="relative">
          <ThreadedChat
            messages={messages}
            onSendMessage={handleSendMessage}
            onMarkResolved={handleMarkResolved}
            onSummarizeThread={handleSummarizeThread}
            onExportMarkdown={handleExportMarkdown}
            onExportPDF={handleExportPDF}
          />
          
          {/* Sandbox toggle button */}
          <IconButton
            aria-label="Toggle sandbox"
            icon={<Icon as={FiMenu} />}
            position="absolute"
            top={4}
            right={4}
            onClick={onToggleSandbox}
            zIndex={2}
          />
        </GridItem>
        
        {/* Right Panel - Agent Sandbox, Tool Output, Checkpoint Approval */}
        <GridItem rowSpan={2} colSpan={1} overflowY="auto" display={isSandboxOpen ? 'block' : 'none'}>
          <AgentSandboxCard
            agentId="orchestrator"
            agentName="Orchestrator"
            status="executing"
            lastMemory="Coordinating agent activities for React state management research"
            activeTool="agent.assign"
            toolkit={["plan.create", "agent.assign", "checkpoint.create"]}
            currentReflection="Planning next steps for implementation phase"
          />
          
          <AgentSandboxCard
            agentId="hal"
            agentName="HAL"
            status="thinking"
            lastMemory="Researching React state management options"
            activeTool="web.search"
            toolkit={["web.search", "code.analyze", "memory.retrieve"]}
            currentReflection="Comparing Context API and Redux performance characteristics"
          />
          
          <ToolOutputCard
            title="Code Example: Context API"
            content={`import React, { createContext, useContext, useState } from 'react';

// Create a context
const CountContext = createContext();

// Provider component
export const CountProvider = ({ children }) => {
  const [count, setCount] = useState(0);
  
  return (
    <CountContext.Provider value={{ count, setCount }}>
      {children}
    </CountContext.Provider>
  );
};

// Custom hook to use the context
export const useCount = () => {
  return useContext(CountContext);
};`}
            type="code"
            language="javascript"
            timestamp={new Date(Date.now() - 1200000)}
          />
          
          <CheckpointApprovalPanel
            checkpoints={checkpoints}
            onApprove={handleApproveCheckpoint}
            onReject={handleRejectCheckpoint}
            onComment={handleCommentCheckpoint}
          />
        </GridItem>
        
        {/* Mobile Drawer for Sandbox */}
        <Drawer
          isOpen={isSandboxOpen}
          placement="right"
          onClose={onToggleSandbox}
          size="md"
        >
          <DrawerOverlay />
          <DrawerContent>
            <DrawerCloseButton />
            <DrawerHeader>Agent Sandbox</DrawerHeader>
            <DrawerBody>
              <AgentSandboxCard
                agentId="orchestrator"
                agentName="Orchestrator"
                status="executing"
                lastMemory="Coordinating agent activities for React state management research"
                activeTool="agent.assign"
                toolkit={["plan.create", "agent.assign", "checkpoint.create"]}
                currentReflection="Planning next steps for implementation phase"
              />
              
              <AgentSandboxCard
                agentId="hal"
                agentName="HAL"
                status="thinking"
                lastMemory="Researching React state management options"
                activeTool="web.search"
                toolkit={["web.search", "code.analyze", "memory.retrieve"]}
                currentReflection="Comparing Context API and Redux performance characteristics"
              />
              
              <ToolOutputCard
                title="Code Example: Context API"
                content={`import React, { createContext, useContext, useState } from 'react';

// Create a context
const CountContext = createContext();

// Provider component
export const CountProvider = ({ children }) => {
  const [count, setCount] = useState(0);
  
  return (
    <CountContext.Provider value={{ count, setCount }}>
      {children}
    </CountContext.Provider>
  );
};

// Custom hook to use the context
export const useCount = () => {
  return useContext(CountContext);
};`}
                type="code"
                language="javascript"
                timestamp={new Date(Date.now() - 1200000)}
              />
              
              <CheckpointApprovalPanel
                checkpoints={checkpoints}
                onApprove={handleApproveCheckpoint}
                onReject={handleRejectCheckpoint}
                onComment={handleCommentCheckpoint}
              />
            </DrawerBody>
          </DrawerContent>
        </Drawer>
        
        {/* Input Area */}
        <GridItem rowSpan={1} colSpan={1}>
          <InputUI
            onSendMessage={handleInputWithFiles}
            placeholder="Type a message..."
          />
        </GridItem>
      </Grid>
    </Box>
  );
};

export default Dashboard;
