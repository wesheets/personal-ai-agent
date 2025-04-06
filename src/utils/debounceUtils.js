/**
 * Utility functions for debouncing and throttling
 */

/**
 * Creates a debounced function that delays invoking func until after wait milliseconds
 * have elapsed since the last time the debounced function was invoked.
 * 
 * @param {Function} func The function to debounce
 * @param {number} wait The number of milliseconds to delay
 * @return {Function} The debounced function
 */
export const debounce = (func, wait) => {
  let timeout;
  
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * Creates a throttled function that only invokes func at most once per every wait milliseconds.
 * 
 * @param {Function} func The function to throttle
 * @param {number} wait The number of milliseconds to throttle invocations to
 * @return {Function} The throttled function
 */
export const throttle = (func, wait) => {
  let lastCall = 0;
  
  return function executedFunction(...args) {
    const now = Date.now();
    
    if (now - lastCall >= wait) {
      func(...args);
      lastCall = now;
    }
  };
};
