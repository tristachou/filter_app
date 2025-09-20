import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api/v1', // Ensure this matches the backend
});

apiClient.interceptors.request.use((config) => {
  // Get the full tokens object from localStorage
  const storedTokens = localStorage.getItem('authTokens');
  
  if (storedTokens) {
    try {
      const tokens = JSON.parse(storedTokens);
      // The access token is typically named AccessToken in the Cognito response
      if (tokens && tokens.AccessToken) {
        config.headers.Authorization = `Bearer ${tokens.AccessToken}`;
      }
    } catch (e) {
      console.error("Could not parse auth tokens from localStorage", e);
    }
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export default apiClient;
