import { useState, useEffect, useCallback } from 'react';

/**
 * Custom hook for fetching data from API endpoints with standardized error handling and loading states
 * 
 * @param {string} url - The API endpoint URL
 * @param {Object} options - Fetch options (method, headers, body, etc.)
 * @param {Object} config - Additional configuration options
 * @param {boolean} config.immediate - Whether to fetch immediately on mount (default: true)
 * @param {Object} config.initialData - Initial data to use before fetch completes
 * @param {number} config.refreshInterval - Interval in ms to automatically refresh data (0 to disable)
 * @param {Function} config.transformResponse - Function to transform the response data
 * @param {Function} config.onSuccess - Callback function to run on successful fetch
 * @param {Function} config.onError - Callback function to run on fetch error
 * @returns {Object} - { data, error, loading, refetch, setData }
 */
const useFetch = (url, options = {}, config = {}) => {
  const {
    immediate = true,
    initialData = null,
    refreshInterval = 0,
    transformResponse = data => data,
    onSuccess = () => {},
    onError = () => {}
  } = config;

  const [data, setData] = useState(initialData);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(immediate);
  const [refreshKey, setRefreshKey] = useState(0);

  // Memoize the fetch function to avoid recreating it on every render
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      
      const response = await fetch(url, options);
      
      if (!response.ok) {
        const errorText = await response.text().catch(() => 'Unknown error');
        throw new Error(`API error (${response.status}): ${errorText}`);
      }
      
      const responseData = await response.json();
      const transformedData = transformResponse(responseData);
      
      setData(transformedData);
      setError(null);
      onSuccess(transformedData);
    } catch (err) {
      console.error(`Error fetching from ${url}:`, err);
      setError(err.message || 'An unknown error occurred');
      onError(err);
      
      // Keep existing data on error if we have it
      if (initialData !== null && data === null) {
        setData(initialData);
      }
    } finally {
      setLoading(false);
    }
  }, [url, options, transformResponse, onSuccess, onError, initialData, data]);

  // Function to manually trigger a refetch
  const refetch = useCallback(() => {
    setRefreshKey(prev => prev + 1);
  }, []);

  // Fetch data when the component mounts or when dependencies change
  useEffect(() => {
    if (!immediate && refreshKey === 0) {
      return;
    }
    
    fetchData();
    
    // Set up automatic refresh interval if specified
    if (refreshInterval > 0) {
      const intervalId = setInterval(fetchData, refreshInterval);
      
      // Clean up interval on unmount
      return () => clearInterval(intervalId);
    }
  }, [fetchData, immediate, refreshInterval, refreshKey]);

  return { data, error, loading, refetch, setData };
};

export default useFetch;
