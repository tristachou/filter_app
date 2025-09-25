import React, { createContext, useContext, useState, useEffect } from 'react';
import { 
  signIn as cognitoSignIn, 
  respondToMfaChallenge, 
  associateSoftwareToken, 
  verifySoftwareToken, 
  updateMfaPreference, // Use the renamed function
  getUser
} from './cognitoAuth';

// 1. Create the context
const AuthContext = createContext(null);

// 2. Create the provider component
export function AuthProvider({ children }) {
  const [tokens, setTokens] = useState(null);
  const [mfaChallenge, setMfaChallenge] = useState(null); // { username, session }
  const [loggedInUsername, setLoggedInUsername] = useState(null);
  const [isMfaEnabled, setIsMfaEnabled] = useState(false);

  // Function to check user's MFA status
  const checkMfaStatus = async (accessToken) => {
    try {
      const userData = await getUser(accessToken);
      // Check if Software Token MFA is present and enabled
      const totpMfa = userData.UserMFASettingList?.includes('SOFTWARE_TOKEN_MFA');
      setIsMfaEnabled(!!totpMfa);
    } catch (error) {
      console.error("Could not fetch user MFA status:", error);
      setIsMfaEnabled(false); // Assume not enabled on error
    }
  };

  // Check for tokens and MFA status on initial render
  useEffect(() => {
    const storedTokens = localStorage.getItem('authTokens');
    const storedUsername = localStorage.getItem('loggedInUsername');
    if (storedTokens && storedUsername) {
      const parsedTokens = JSON.parse(storedTokens);
      setTokens(parsedTokens);
      setLoggedInUsername(storedUsername);
      checkMfaStatus(parsedTokens.AccessToken); // Check MFA status on load
    }
  }, []);

  const handleSuccessfulLogin = (authResult, username) => {
    setTokens(authResult);
    setLoggedInUsername(username);
    localStorage.setItem('authTokens', JSON.stringify(authResult));
    localStorage.setItem('loggedInUsername', username);
    checkMfaStatus(authResult.AccessToken); // Check MFA status after login
  };

  const login = async (username, password) => {
    logout(); 
    try {
      const authResult = await cognitoSignIn(username, password);
      if (authResult.challengeName === 'SOFTWARE_TOKEN_MFA') {
        setMfaChallenge({ username, session: authResult.session });
      } else if (authResult.AccessToken) {
        handleSuccessfulLogin(authResult, username);
      } else {
        throw new Error("Unexpected authentication result.");
      }
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const verifyMfa = async (mfaCode) => {
    if (!mfaChallenge) throw new Error("MFA challenge not initiated.");
    try {
      const { username, session } = mfaChallenge;
      const authResult = await respondToMfaChallenge(username, mfaCode, session);
      handleSuccessfulLogin(authResult, username);
      setMfaChallenge(null);
    } catch (error) {
      console.error('MFA verification failed:', error);
      throw error;
    }
  };

  const setupMfa = async () => {
    if (!tokens) throw new Error("User is not authenticated.");
    return await associateSoftwareToken(tokens.AccessToken);
  };

  const finalizeMfa = async (userCode) => {
    if (!tokens) throw new Error("User is not authenticated.");
    await verifySoftwareToken(tokens.AccessToken, userCode);
    await updateMfaPreference(tokens.AccessToken, { Enabled: true, PreferredMfa: true });
    setIsMfaEnabled(true); // Manually update state after enabling
  };

  const disableMfa = async () => {
    if (!tokens) throw new Error("User is not authenticated.");
    await updateMfaPreference(tokens.AccessToken, { Enabled: false, PreferredMfa: false });
    setIsMfaEnabled(false); // Manually update state after disabling
  };

  const logout = () => {
    setTokens(null);
    setMfaChallenge(null);
    setLoggedInUsername(null);
    setIsMfaEnabled(false);
    localStorage.removeItem('authTokens');
    localStorage.removeItem('loggedInUsername');
  };

  const authValue = {
    tokens,
    username: loggedInUsername,
    isAuthenticated: !!tokens,
    isMfaEnabled,
    mfaRequired: !!mfaChallenge,
    mfaChallenge,
    login,
    verifyMfa,
    logout,
    setupMfa,
    finalizeMfa,
    disableMfa,
  };

  return (
    <AuthContext.Provider value={authValue}>
      {children}
    </AuthContext.Provider>
  );
}

// 3. Create a custom hook for easy consumption
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
