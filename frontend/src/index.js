import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css'; // Asegúrate de que Tailwind esté aquí o usa un CDN en el HTML
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

/*
Tailwind: Para que el diseño del App.js que te di funcione, añade esta línea en tu frontend/public/index.html dentro del <head>:
<script src="https://cdn.tailwindcss.com"></script>
*/
