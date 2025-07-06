import React, { useState, useEffect } from 'react';
import api from './api'; // We'll create this api helper next
import './App.css';

function App() {
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchMessage = async () => {
      try {
        const response = await api.get('/'); // Using the /api prefix defined in setupProxy.js or environment variable for production
        setMessage(response.data.message);
      } catch (err) {
        console.error("Error fetching data from backend:", err);
        let errorMessage = 'Failed to fetch message from backend.';
        if (err.response) {
          // The request was made and the server responded with a status code
          // that falls out of the range of 2xx
          errorMessage += ` Status: ${err.response.status} - ${err.response.statusText}.`;
          if (err.response.data && err.response.data.detail) {
            errorMessage += ` Detail: ${JSON.stringify(err.response.data.detail)}.`;
          } else if (err.response.data && err.response.data.message) {
            errorMessage += ` Message: ${err.response.data.message}.`;
          }
        } else if (err.request) {
          // The request was made but no response was received
          errorMessage += ' No response received from server. Is the backend running and accessible?';
        } else {
          // Something happened in setting up the request that triggered an Error
          errorMessage += ` Error: ${err.message}.`;
        }
        setError(errorMessage);
        setMessage(''); // Clear any previous message
      }
    };

    fetchMessage();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>MentorAI Frontend</h1>
        {message && <p>Message from backend: <strong>{message}</strong></p>}
        {error && <p style={{ color: 'red' }}>Error: {error}</p>}
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

export default App;
