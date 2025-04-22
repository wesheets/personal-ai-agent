import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './css/index.css'

// Add dark mode class to html element
document.documentElement.classList.add('dark')

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
