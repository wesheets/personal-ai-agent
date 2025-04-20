import React from 'react'
import ReactDOM from 'react-dom/client'
import OperatorConsole from '../components/OperatorConsole'
import '../css/index.css'

// Add dark mode class to html element
document.documentElement.classList.add('dark')

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <OperatorConsole />
  </React.StrictMode>,
)
