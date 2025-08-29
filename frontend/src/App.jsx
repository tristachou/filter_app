import React, { useState, useEffect } from 'react';
import apiClient from './apiClient';
import LoginView from './components/LoginView';
import AppView from './components/AppView'; // Import the new component
import './index.css';

function App() {
  const [token, setToken] = useState(localStorage.getItem('jwt_token'));
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');

  useEffect(() => {
    const storedToken = localStorage.getItem('jwt_token');
    if (storedToken) {
      setToken(storedToken);
    }
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError('');
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await apiClient.post('/auth/token', formData);
      const new_token = response.data.access_token;
      localStorage.setItem('jwt_token', new_token);
      setToken(new_token);
    } catch (error) {
      setLoginError('Invalid credentials. Please try again.');
      console.error('Login failed:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('jwt_token');
    setToken(null);
  };

  return (
    <div id="app-container">
      {token ? (
        <AppView handleLogout={handleLogout} /> // Use the new component
      ) : (
        <LoginView
          handleLogin={handleLogin}
          username={username}
          setUsername={setUsername}
          password={password}
          setPassword={setPassword}
          loginError={loginError}
        />
      )}
    </div>
  );
}

export default App;