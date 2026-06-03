import React from 'react';
import ReactDOM from 'react-dom/client';
import InitColorSchemeScript from '@mui/material/InitColorSchemeScript';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

const root = ReactDOM.createRoot(document.getElementById('root')!);
root.render(
  <React.StrictMode>
    <InitColorSchemeScript defaultMode="dark" attribute="data-mui-color-scheme" />
    <App />
  </React.StrictMode>
);

reportWebVitals();

