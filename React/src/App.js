import { Route, Routes, useNavigate } from 'react-router-dom';
import Home from './home';
import Login from './login';
import Register from './register';
import './App.css';
import { useEffect, useState } from 'react';
import Dashboard from './dashboard';  // Import the Dashboard component
import Verify from './verify';  // Make sure to import Verify here

function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [email, setEmail] = useState('');

  const navigate = useNavigate();

  useEffect(() => {
    if (loggedIn) {
      navigate('/dashboard');
    }
  }, [loggedIn, navigate]);

  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<Home email={email} loggedIn={loggedIn} setLoggedIn={setLoggedIn} />} />
        <Route path="/login" element={<Login setLoggedIn={setLoggedIn} setEmail={setEmail} />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/verify/:token" element={<Verify />} /> {/* Add the Verify route */}
      </Routes>
    </div>
  );
}

export default App;