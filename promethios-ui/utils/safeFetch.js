// Safe fetch utility for Promethios UI
// Provides error handling and timeout functionality

/**
 * Enhanced fetch with timeout and error handling
 * @param {string} url - The URL to fetch
 * @param {Object} options - Fetch options
 * @param {number} timeout - Timeout in milliseconds
 * @returns {Promise} - Promise that resolves to the fetch response
 */
const safeFetch = async (url, options = {}, timeout = 30000) => {
  // Create abort controller for timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  try {
    // Add signal to options
    const fetchOptions = {
      ...options,
      signal: controller.signal
    };
    
    // Perform fetch
    const response = await fetch(url, fetchOptions);
    
    // Clear timeout
    clearTimeout(timeoutId);
    
    // Check if response is ok
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
    }
    
    // Return response
    return response;
  } catch (error) {
    // Clear timeout
    clearTimeout(timeoutId);
    
    // Handle specific errors
    if (error.name === 'AbortError') {
      console.error(`Request timeout after ${timeout}ms: ${url}`);
      throw new Error(`Request timeout after ${timeout}ms`);
    }
    
    // Log and rethrow other errors
    console.error(`Fetch error for ${url}:`, error);
    throw error;
  }
};

/**
 * Safe JSON fetch with error handling
 * @param {string} url - The URL to fetch
 * @param {Object} options - Fetch options
 * @param {number} timeout - Timeout in milliseconds
 * @returns {Promise} - Promise that resolves to the parsed JSON
 */
safeFetch.json = async (url, options = {}, timeout = 30000) => {
  try {
    const response = await safeFetch(url, options, timeout);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(`JSON parse error for ${url}:`, error);
    throw error;
  }
};

/**
 * Safe text fetch with error handling
 * @param {string} url - The URL to fetch
 * @param {Object} options - Fetch options
 * @param {number} timeout - Timeout in milliseconds
 * @returns {Promise} - Promise that resolves to the text content
 */
safeFetch.text = async (url, options = {}, timeout = 30000) => {
  try {
    const response = await safeFetch(url, options, timeout);
    const text = await response.text();
    return text;
  } catch (error) {
    console.error(`Text fetch error for ${url}:`, error);
    throw error;
  }
};

export default safeFetch;
