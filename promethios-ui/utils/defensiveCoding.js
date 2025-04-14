import React from 'react';

// Utility function to safely map over arrays with null/undefined filtering
export const safeMap = (array, mapFn) => {
  if (!array || !Array.isArray(array)) return [];
  return array.filter(item => item !== null && item !== undefined).map(mapFn);
};

// Utility function to safely access nested properties
export const safeGet = (obj, path, defaultValue = null) => {
  if (!obj) return defaultValue;
  
  const keys = path.split('.');
  let result = obj;
  
  for (const key of keys) {
    if (result === null || result === undefined) {
      return defaultValue;
    }
    result = result[key];
  }
  
  return result !== undefined ? result : defaultValue;
};

// Utility function to safely join classnames, filtering out falsy values
export const safeClassNames = (...classes) => {
  return classes.filter(Boolean).join(' ');
};

// Utility function to safely parse JSON
export const safeJsonParse = (jsonString, defaultValue = {}) => {
  if (!jsonString) return defaultValue;
  
  try {
    return JSON.parse(jsonString);
  } catch (error) {
    console.error('Error parsing JSON:', error);
    return defaultValue;
  }
};

// Utility function to safely format dates
export const safeFormatDate = (dateString, format = 'default') => {
  if (!dateString) return 'Unknown date';
  
  try {
    const date = new Date(dateString);
    
    if (isNaN(date.getTime())) {
      return 'Invalid date';
    }
    
    switch (format) {
      case 'time':
        return date.toLocaleTimeString();
      case 'date':
        return date.toLocaleDateString();
      case 'datetime':
        return date.toLocaleString();
      default:
        return date.toLocaleString();
    }
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'Unknown date';
  }
};

// Defensive rendering HOC
export const withDefensiveRendering = (Component) => {
  return function DefensiveComponent(props) {
    try {
      return <Component {...props} />;
    } catch (error) {
      console.error('Error rendering component:', error);
      return (
        <div style={{ padding: '10px', color: 'red', backgroundColor: '#ffeeee', borderRadius: '4px' }}>
          Component Error: {error.message}
        </div>
      );
    }
  };
};
