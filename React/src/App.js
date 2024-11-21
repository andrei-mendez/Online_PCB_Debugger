// src/App.js
import { Route, Routes, useNavigate } from 'react-router-dom';
import Home from './home';
import Login from './login';
import Register from './register';
import './App.css';
import { useEffect, useState } from 'react';
import Dashboard from './dashboard';  // Import the Dashboard component

function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [email, setEmail] = useState('');

  const navigate = useNavigate();  // Initialize the navigate function

  // UseEffect hook to redirect if the user is logged in
  useEffect(() => {
    if (loggedIn) {
      navigate('/dashboard');  // Redirect to the dashboard if logged in
    }
  }, [loggedIn, navigate]);  // Depend on `loggedIn` so it runs when the state changes

  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<Home email={email} loggedIn={loggedIn} setLoggedIn={setLoggedIn} />} />
        <Route path="/login" element={<Login setLoggedIn={setLoggedIn} setEmail={setEmail} />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Dashboard />} />  {/* Dashboard route */}
      </Routes>
    </div>
  );
}

export default App;
