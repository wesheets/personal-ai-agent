/**
 * Utility function to verify user credentials
 * Required for the login system via environment variables
 */

export interface Credentials {
  username: string;
  password: string;
}

/**
 * Verifies user credentials against environment variables
 * @param credentials User credentials to verify
 * @returns Boolean indicating if credentials are valid
 */
export const verifyCredentials = (credentials: Credentials): boolean => {
  const { username, password } = credentials;
  
  // Get operator credentials from environment variables
  const operatorUsername = import.meta.env.VITE_OPERATOR_USERNAME || '';
  const operatorPassword = import.meta.env.VITE_OPERATOR_PASSWORD || '';
  
  // Verify credentials match
  return username === operatorUsername && password === operatorPassword;
};

export default verifyCredentials;
