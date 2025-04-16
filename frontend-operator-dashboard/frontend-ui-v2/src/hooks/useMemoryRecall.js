// src/hooks/useMemoryRecall.js

/**
 * Gets the most recent memory from the memories array
 * @param {Array} memories - Array of memory objects
 * @returns {Object|null} - The most recent memory or null if no memories exist
 */
export const getLatestMemory = (memories) => {
  return memories.length ? memories[memories.length - 1] : null;
};

/**
 * Injects context from the latest memory into the current input
 * @param {string} input - The current user input
 * @param {Array} memories - Array of memory objects
 * @returns {string} - Input with context from the latest memory if available
 */
export const injectContext = (input, memories) => {
  const last = getLatestMemory(memories);
  return last ? `You previously said: "${last.content}". Now respond to: ${input}` : input;
};
