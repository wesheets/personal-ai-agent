import React, { createContext, useContext, useState, ReactNode } from 'react';

interface ApiContextType {
  apiBaseUrl: string;
  setApiBaseUrl: (url: string) => void;
}

const defaultApiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const ApiContext = createContext<ApiContextType>({
  apiBaseUrl: defaultApiBaseUrl,
  setApiBaseUrl: () => {},
});

export const ApiProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [apiBaseUrl, setApiBaseUrl] = useState<string>(defaultApiBaseUrl);

  return (
    <ApiContext.Provider value={{ apiBaseUrl, setApiBaseUrl }}>
      {children}
    </ApiContext.Provider>
  );
};

export const useApi = () => useContext(ApiContext);
