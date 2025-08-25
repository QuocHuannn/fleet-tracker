/**
 * Fleet Tracker Frontend Entry Point
 * 
 * Author: Trương Quốc Huân
 * Email: truonghuan0709@gmail.com
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App.tsx';
import reportWebVitals from './reportWebVitals.ts';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Performance measuring
// Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
