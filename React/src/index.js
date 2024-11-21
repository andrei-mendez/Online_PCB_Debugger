// src/index.js or src/index.tsx
import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import { BrowserRouter } from 'react-router-dom';  // Import BrowserRouter

ReactDOM.render(
  <BrowserRouter>  {/* Wrap App with BrowserRouter */}
    <App />
  </BrowserRouter>,
  document.getElementById('root')
);