import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Flex,
  Text,
  VStack,
  HStack,
  Input,
  IconButton,
  Avatar,
  useColorModeValue,
  Divider,
  Spinner,
  Button,
  Textarea,
  useToast,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Tooltip
} from '@chakra-ui/react';
import { 
  FiSend, 
  FiPaperclip, 
  FiMoreVertical, 
  FiRefreshCw, 
  FiCopy, 
  FiTrash2,
  FiMic,
  FiStopCircle
} from 'react-icons/fi';
import { useAuth } from '../context/AuthContext';

// Message type definition
const MessageType = {
  USER: 'user',
  AGENT: 'agent',
  SYSTEM: 'system',
  ERROR: 'error'
};

const AgentChatPanel = ({ 
  agentId, 
  agentName = 'Agent', 
  agentAvatar = '', 
  isSystemAgent = false,
  onNewConversation = () => {},
  onSendMessage = async () => {},
  onStreamMessage = async () => {}
}) => {
  const { user } = useAuth();
  const toast = useToast();
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  
  // States
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentStreamedMessage, setCurrentStreamedMessage] = useState('');
  const [attachments, setAttachments] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  
  // Colors
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const userBubbleBg = useColorModeValue('blue.500', 'blue.500');
  const userBubbleColor = 'white';
  const agentBubbleBg = useColorModeValue('gray.100', 'gray.700');
  const agentBubbleColor = useColorModeValue('gray.800', 'white');
  const systemBubbleBg = useColorModeValue('gray.200', 'gray.600');
  const systemBubbleColor = useColorModeValue('gray.700', 'gray.100');
  const errorBubbleBg = useColorModeValue('red.100', 'red.900');
  const errorBubbleColor = useColorModeValue('red.700', 'red.200');
  
  // Generate avatar background color based on name
  const getAvatarBg = (name) => {
    if (!name) return 'blue.500';
    const colors = ['red', 'orange', 'yellow', 'green', 'teal', 'blue', 'cyan', 'purple', 'pink'];
    const hash = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return `${colors[hash % colors.length]}.500`;
  };
  
  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  // Effect to scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages, currentStreamedMessage]);
  
  // Effect to load conversation history
  useEffect(() => {
    const loadConversation = async () => {
      if (!agentId) return;
      
      setIsLoading(true);
      
      try {
        // Fetch conversation history from API
        const response = await fetch(`/api/conversations/${agentId}/latest`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (!response.ok) {
          throw new Error('Failed to load conversation');
        }
        
        const data = await response.json();
        
        if (data.conversation) {
          setConversationId(data.conversation.id);
          setMessages(data.conversation.messages || []);
        } else {
          // Start a new conversation
          setMessages([
            {
              id: 'welcome',
              type: MessageType.SYSTEM,
              content: `Welcome to a conversation with ${agentName}. How can I assist you today?`,
              timestamp: new Date().toISOString()
            }
          ]);
        }
      } catch (err) {
        console.error('Error loading conversation:', err);
        setMessages([
          {
            id: 'welcome',
            type: MessageType.SYSTEM,
            content: `Welcome to a conversation with ${agentName}. How can I assist you today?`,
            timestamp: new Date().toISOString()
          }
        ]);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadConversation();
  }, [agentId, agentName]);
  
  // Handle sending a message
  const handleSendMessage = async () => {
    if (!inputValue.trim() && attachments.length === 0) return;
    
    const messageContent = inputValue.trim();
    setInputValue('');
    
    // Add user message to the UI immediately
    const userMessage = {
      id: `user-${Date.now()}`,
      type: MessageType.USER,
      content: messageContent,
      attachments: [...attachments],
      timestamp: new Date().toISOString(),
      sender: {
        id: user?.id || 'user',
        name: user?.name || 'You',
        avatar: user?.avatar || ''
      }
    };
    
    setMessages(prev => [...prev, userMessage]);
    setAttachments([]);
    
    // Show typing indicator
    setIsStreaming(true);
    setCurrentStreamedMessage('');
    
    try {
      // If using streaming
      const streamController = new AbortController();
      const { signal } = streamController;
      
      // Start streaming response
      const streamResponse = await onStreamMessage({
        conversationId,
        message: messageContent,
        attachments: attachments,
        signal
      });
      
      // Process the stream
      if (streamResponse && streamResponse.stream) {
        const reader = streamResponse.stream.getReader();
        
        let accumulatedMessage = '';
        
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) {
            break;
          }
          
          // Decode the chunk and append to accumulated message
          const chunk = new TextDecoder().decode(value);
          accumulatedMessage += chunk;
          setCurrentStreamedMessage(accumulatedMessage);
        }
        
        // Add the complete agent message
        const agentMessage = {
          id: `agent-${Date.now()}`,
          type: MessageType.AGENT,
          content: accumulatedMessage,
          timestamp: new Date().toISOString(),
          sender: {
            id: agentId,
            name: agentName,
            avatar: agentAvatar
          }
        };
        
        setMessages(prev => [...prev, agentMessage]);
        setCurrentStreamedMessage('');
        
        // Update conversation ID if this is a new conversation
        if (!conversationId && streamResponse.conversationId) {
          setConversationId(streamResponse.conversationId);
        }
      } else {
        // Fallback to non-streaming response
        const response = await onSendMessage({
          conversationId,
          message: messageContent,
          attachments: attachments
        });
        
        if (response && response.message) {
          const agentMessage = {
            id: `agent-${Date.now()}`,
            type: MessageType.AGENT,
            content: response.message,
            timestamp: new Date().toISOString(),
            sender: {
              id: agentId,
              name: agentName,
              avatar: agentAvatar
            }
          };
          
          setMessages(prev => [...prev, agentMessage]);
          
          // Update conversation ID if this is a new conversation
          if (!conversationId && response.conversationId) {
            setConversationId(response.conversationId);
          }
        }
      }
    } catch (err) {
      console.error('Error sending message:', err);
      
      // Add error message
      const errorMessage = {
        id: `error-${Date.now()}`,
        type: MessageType.ERROR,
        content: 'Sorry, there was an error processing your request. Please try again.',
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsStreaming(false);
    }
  };
  
  // Handle file attachment
  const handleAttachment = () => {
    fileInputRef.current?.click();
  };
  
  // Handle file selection
  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    
    if (files.length > 0) {
      const newAttachments = files.map(file => ({
        id: `attachment-${Date.now()}-${file.name}`,
        name: file.name,
        type: file.type,
        size: file.size,
        file
      }));
      
      setAttachments(prev => [...prev, ...newAttachments]);
      
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };
  
  // Handle removing an attachment
  const handleRemoveAttachment = (attachmentId) => {
    setAttachments(prev => prev.filter(a => a.id !== attachmentId));
  };
  
  // Handle starting a new conversation
  const handleNewConversation = () => {
    setMessages([
      {
        id: 'welcome',
        type: MessageType.SYSTEM,
        content: `Starting a new conversation with ${agentName}. How can I assist you today?`,
        timestamp: new Date().toISOString()
      }
    ]);
    setConversationId(null);
    onNewConversation();
  };
  
  // Handle copying message content
  const handleCopyMessage = (content) => {
    navigator.clipboard.writeText(content)
      .then(() => {
        toast({
          title: 'Copied to clipboard',
          status: 'success',
          duration: 2000,
          isClosable: true,
          position: 'top'
        });
      })
      .catch(err => {
        console.error('Failed to copy:', err);
        toast({
          title: 'Failed to copy',
          status: 'error',
          duration: 2000,
          isClosable: true,
          position: 'top'
        });
      });
  };
  
  // Format message timestamp
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };
  
  return (
    <Box
      h="100%"
      display="flex"
      flexDirection="column"
      borderWidth="1px"
      borderColor={borderColor}
      borderRadius="lg"
      overflow="hidden"
      bg={bgColor}
    >
      {/* Chat header */}
      <Flex
        p={4}
        borderBottomWidth="1px"
        borderColor={borderColor}
        alignItems="center"
        justifyContent="space-between"
      >
        <HStack spacing={3}>
          <Avatar 
            size="sm" 
            name={agentName} 
            src={agentAvatar} 
            bg={getAvatarBg(agentName)}
          />
          <Box>
            <Text fontWeight="bold">{agentName}</Text>
            {isSystemAgent && (
              <Text fontSize="xs" color="gray.500">
                System Agent
              </Text>
            )}
          </Box>
        </HStack>
        
        <Menu>
          <MenuButton
            as={IconButton}
            icon={<FiMoreVertical />}
            variant="ghost"
            size="sm"
            aria-label="Chat options"
          />
          <MenuList>
            <MenuItem icon={<FiRefreshCw />} onClick={handleNewConversation}>
              New Conversation
            </MenuItem>
            <MenuItem icon={<FiCopy />} onClick={() => handleCopyMessage(messages.map(m => `${m.sender?.name || 'System'}: ${m.content}`).join('\n\n'))}>
              Copy Conversation
            </MenuItem>
            <MenuItem icon={<FiTrash2 />} color="red.500">
              Clear History
            </MenuItem>
          </MenuList>
        </Menu>
      </Flex>
      
      {/* Messages area */}
      <Box
        flex="1"
        overflowY="auto"
        p={4}
        css={{
          '&::-webkit-scrollbar': {
            width: '4px',
          },
          '&::-webkit-scrollbar-track': {
            width: '6px',
          },
          '&::-webkit-scrollbar-thumb': {
            background: borderColor,
            borderRadius: '24px',
          },
        }}
      >
        {isLoading ? (
          <Flex justify="center" align="center" h="100%">
            <Spinner size="xl" color="blue.500" />
          </Flex>
        ) : (
          <VStack spacing={4} align="stretch">
            {messages.map((message) => (
              <Box key={message.id}>
                {message.type === MessageType.USER ? (
                  <HStack spacing={2} alignItems="flex-start" justifyContent="flex-end">
                    <Menu>
                      <MenuButton
                        as={IconButton}
                        icon={<FiMoreVertical />}
                        variant="ghost"
                        size="xs"
                        aria-label="Message options"
                      />
                      <MenuList>
                        <MenuItem icon={<FiCopy />} onClick={() => handleCopyMessage(message.content)}>
                          Copy Message
                        </MenuItem>
                      </MenuList>
                    </Menu>
                    
                    <Box
                      maxW="70%"
                      p={3}
                      borderRadius="lg"
                      borderTopRightRadius="sm"
                      bg={userBubbleBg}
                      color={userBubbleColor}
                    >
                      <Text>{message.content}</Text>
                      
                      {message.attachments && message.attachments.length > 0 && (
                        <VStack mt={2} spacing={1} align="stretch">
                          {message.attachments.map(attachment => (
                            <HStack 
                              key={attachment.id} 
                              bg="rgba(255,255,255,0.2)" 
                              p={1} 
                              borderRadius="md"
                              fontSize="xs"
                            >
                              <FiPaperclip />
                              <Text noOfLines={1}>{attachment.name}</Text>
                            </HStack>
                          ))}
                        </VStack>
                      )}
                      
                      <Text fontSize="xs" textAlign="right" mt={1} opacity={0.8}>
                        {formatTimestamp(message.timestamp)}
                      </Text>
                    </Box>
                    
                    <Avatar 
                      size="sm" 
                      name={message.sender?.name} 
                      src={message.sender?.avatar} 
                    />
                  </HStack>
                ) : message.type === MessageType.AGENT ? (
                  <HStack spacing={2} alignItems="flex-start">
                    <Avatar 
                      size="sm" 
                      name={message.sender?.name || agentName} 
                      src={message.sender?.avatar || agentAvatar} 
                      bg={getAvatarBg(message.sender?.name || agentName)}
                    />
                    
                    <Box
                      maxW="70%"
                      p={3}
                      borderRadius="lg"
                      borderTopLeftRadius="sm"
                      bg={agentBubbleBg}
                      color={agentBubbleColor}
                    >
                      <Text whiteSpace="pre-wrap">{message.content}</Text>
                      
                      <Text fontSize="xs" textAlign="right" mt={1} opacity={0.8}>
                        {formatTimestamp(message.timestamp)}
                      </Text>
                    </Box>
                    
                    <Menu>
                      <MenuButton
                        as={IconButton}
                        icon={<FiMoreVertical />}
                        variant="ghost"
                        size="xs"
                        aria-label="Message options"
                      />
                      <MenuList>
                        <MenuItem icon={<FiCopy />} onClick={() => handleCopyMessage(message.content)}>
                          Copy Message
                        </MenuItem>
                      </MenuList>
                    </Menu>
                  </HStack>
                ) : message.type === MessageType.ERROR ? (
                  <Box
                    maxW="100%"
                    p={3}
                    borderRadius="lg"
                    bg={errorBubbleBg}
                    color={errorBubbleColor}
                    mx="auto"
                  >
                    <Text>{message.content}</Text>
                    
                    <Text fontSize="xs" textAlign="right" mt={1} opacity={0.8}>
                      {formatTimestamp(message.timestamp)}
                    </Text>
                  </Box>
                ) : (
                  <Box
                    maxW="100%"
                    p={3}
                    borderRadius="lg"
                    bg={systemBubbleBg}
                    color={systemBubbleColor}
                    mx="auto"
                  >
                    <Text>{message.content}</Text>
                    
                    <Text fontSize="xs" textAlign="right" mt={1} opacity={0.8}>
                      {formatTimestamp(message.timestamp)}
                    </Text>
                  </Box>
                )}
              </Box>
            ))}
            
            {/* Streaming message */}
            {isStreaming && currentStreamedMessage && (
              <HStack spacing={2} alignItems="flex-start">
                <Avatar 
                  size="sm" 
                  name={agentName} 
                  src={agentAvatar} 
                  bg={getAvatarBg(agentName)}
                />
                
                <Box
                  maxW="70%"
                  p={3}
                  borderRadius="lg"
                  borderTopLeftRadius="sm"
                  bg={agentBubbleBg}
                  color={agentBubbleColor}
                >
                  <Text whiteSpace="pre-wrap">{currentStreamedMessage}</Text>
                  
                  <HStack spacing={1} mt={2}>
                    <Spinner size="xs" />
                    <Text fontSize="xs">Typing...</Text>
                  </HStack>
                </Box>
              </HStack>
            )}
            
            {/* Typing indicator without content */}
            {isStreaming && !currentStreamedMessage && (
              <HStack spacing={2} alignItems="flex-start">
                <Avatar 
                  size="sm" 
                  name={agentName} 
                  src={agentAvatar} 
                  bg={getAvatarBg(agentName)}
                />
                
                <Box
                  p={3}
                  borderRadius="lg"
                  borderTopLeftRadius="sm"
                  bg={agentBubbleBg}
                  color={agentBubbleColor}
                >
                  <HStack spacing={1}>
                    <Spinner size="xs" />
                    <Text fontSize="sm">Thinking...</Text>
                  </HStack>
                </Box>
              </HStack>
            )}
            
            {/* Invisible element to scroll to */}
            <div ref={messagesEndRef} />
          </VStack>
        )}
      </Box>
      
      {/* Attachments area */}
      {attachments.length > 0 && (
        <Box p={2} borderTopWidth="1px" borderColor={borderColor}>
          <HStack spacing={2} overflowX="auto" py={1} px={2}>
            {attachments.map(attachment => (
              <HStack 
                key={attachment.id} 
                bg={useColorModeValue('gray.100', 'gray.700')} 
                p={2} 
                borderRadius="md"
                fontSize="sm"
              >
                <FiPaperclip />
                <Text noOfLines={1} maxW="150px">{attachment.name}</Text>
                <IconButton
                  icon={<FiX />}
                  size="xs"
                  variant="ghost"
                  aria-label="Remove attachment"
                  onClick={() => handleRemoveAttachment(attachment.id)}
                />
              </HStack>
            ))}
          </HStack>
        </Box>
      )}
      
      {/* Input area */}
      <Box p={4} borderTopWidth="1px" borderColor={borderColor}>
        <HStack spacing={2}>
          <Tooltip label="Attach file">
            <IconButton
              icon={<FiPaperclip />}
              aria-label="Attach file"
              variant="ghost"
              onClick={handleAttachment}
              isDisabled={isStreaming}
            />
          </Tooltip>
          
          <Input
            type="file"
            ref={fileInputRef}
            display="none"
            onChange={handleFileChange}
            multiple
          />
          
          <Textarea
            placeholder="Type your message..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
            resize="none"
            rows={1}
            maxRows={5}
            disabled={isStreaming}
          />
          
          <Tooltip label={isStreaming ? "Stop generating" : "Send message"}>
            <IconButton
              icon={isStreaming ? <FiStopCircle /> : <FiSend />}
              colorScheme={isStreaming ? "red" : "blue"}
              aria-label={isStreaming ? "Stop generating" : "Send message"}
              onClick={isStreaming ? () => {} : handleSendMessage}
              isDisabled={!inputValue.trim() && attachments.length === 0 && !isStreaming}
            />
          </Tooltip>
        </HStack>
      </Box>
    </Box>
  );
};

export default AgentChatPanel;
