/**
 * Safe fetch utility with timeout, abort controller, and error handling
 * For use across Dashboard, Memory, and Agent pages
 */

/**
 * Performs a fetch request with timeout and error handling
 * 
 * @param {string} url - The URL to fetch
 * @param {Function} setData - State setter function for successful data
 * @param {Function} setError - State setter function for error state
 * @param {number} timeout - Timeout in milliseconds (default: 8000)
 * @returns {Promise<void>}
 */
export async function safeFetch(url, setData, setError, timeout = 8000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);

  try {
    const res = await fetch(url, { signal: controller.signal });
    
    if (!res.ok) {
      throw new Error(`Server responded with status: ${res.status}`);
    }
    
    const data = await res.json();
    setData(data);
  } catch (err) {
    console.error("Fetch error:", err);
    setError(true);
  } finally {
    clearTimeout(timer);
  }
}

export default safeFetch;
