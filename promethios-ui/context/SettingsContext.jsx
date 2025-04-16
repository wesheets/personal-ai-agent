import React, { createContext, useContext, useState, useEffect } from 'react';

// Default settings
const DEFAULT_SETTINGS = {
  debugMode: false,
  showFallbackAlerts: true,
  autoRefreshPanels: true
};

// Create context
const SettingsContext = createContext();

/**
 * SettingsProvider Component
 *
 * Provides global access to application settings
 * Persists settings to localStorage
 */
export const SettingsProvider = ({ children }) => {
  // Initialize settings state from localStorage or defaults
  const [settings, setSettings] = useState(() => {
    try {
      const storedSettings = localStorage.getItem('promethiosSettings');
      return storedSettings ? JSON.parse(storedSettings) : DEFAULT_SETTINGS;
    } catch (error) {
      console.error('Error loading settings from localStorage:', error);
      return DEFAULT_SETTINGS;
    }
  });

  // Update localStorage when settings change
  useEffect(() => {
    try {
      localStorage.setItem('promethiosSettings', JSON.stringify(settings));
    } catch (error) {
      console.error('Error saving settings to localStorage:', error);
    }
  }, [settings]);

  /**
   * Update a specific setting
   * @param {string} key - Setting key
   * @param {any} value - Setting value
   */
  const updateSetting = (key, value) => {
    setSettings((prev) => ({
      ...prev,
      [key]: value
    }));
  };

  /**
   * Reset settings to defaults
   */
  const resetSettings = () => {
    setSettings(DEFAULT_SETTINGS);
  };

  // Context value
  const value = {
    settings,
    updateSetting,
    resetSettings
  };

  return <SettingsContext.Provider value={value}>{children}</SettingsContext.Provider>;
};

/**
 * Custom hook to use the settings context
 */
export const useSettings = () => {
  const context = useContext(SettingsContext);

  if (!context) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }

  return context;
};

export default SettingsContext;
