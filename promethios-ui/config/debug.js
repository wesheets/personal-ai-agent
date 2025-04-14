// Debug configuration for Promethios UI
const debug = {
  enabled: false,
  logLevel: 'info',
  showDevTools: false,
  
  // Enable debug mode
  enable: () => {
    debug.enabled = true;
    console.log('Debug mode enabled');
    return debug;
  },
  
  // Disable debug mode
  disable: () => {
    debug.enabled = false;
    console.log('Debug mode disabled');
    return debug;
  },
  
  // Set log level
  setLogLevel: (level) => {
    debug.logLevel = level;
    console.log(`Log level set to: ${level}`);
    return debug;
  },
  
  // Toggle dev tools
  toggleDevTools: () => {
    debug.showDevTools = !debug.showDevTools;
    console.log(`Dev tools ${debug.showDevTools ? 'enabled' : 'disabled'}`);
    return debug;
  },
  
  // Log message with level
  log: (message, level = 'info') => {
    if (!debug.enabled) return;
    
    if (level === 'error') {
      console.error(`[PROMETHIOS:ERROR] ${message}`);
    } else if (level === 'warn') {
      console.warn(`[PROMETHIOS:WARN] ${message}`);
    } else {
      console.log(`[PROMETHIOS:INFO] ${message}`);
    }
  }
};

export default debug;
