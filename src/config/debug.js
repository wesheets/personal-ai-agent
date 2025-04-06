// Debug mode configuration
// Set to false for production, true for development
// This controls polling behavior across the application
const DEBUG_MODE = process.env.NODE_ENV === 'development';

// Console debug logging function that only logs in debug mode
export const debugLog = (component, message, type = 'info') => {
  if (!DEBUG_MODE) return;
  
  const timestamp = new Date().toLocaleTimeString();
  const prefix = `[${timestamp}][${component}]`;
  
  switch (type) {
    case 'error':
      console.error(`${prefix} ❌ ${message}`);
      break;
    case 'warn':
      console.warn(`${prefix} ⚠️ ${message}`);
      break;
    case 'success':
      console.log(`${prefix} ✅ ${message}`);
      break;
    case 'info':
    default:
      console.debug(`${prefix} ℹ️ ${message}`);
  }
};

export default DEBUG_MODE;
