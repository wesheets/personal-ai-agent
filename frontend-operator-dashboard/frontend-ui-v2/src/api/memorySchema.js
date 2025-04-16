// src/api/memorySchema.js
export const createMemory = ({
  user = 'admin',
  agent = 'HAL',
  type = 'task',
  content = '',
  tags = [],
  visibility = 'private'
}) => ({
  id: crypto.randomUUID(),
  timestamp: new Date().toISOString(),
  user,
  agent,
  type,
  content,
  tags,
  visibility
});
