# Final UI Patch Tasks

## Issues to Fix
- [x] Hook Up MemoryWarningHandler.jsx
  - [x] Inject into MemoryBrowser.jsx
  - [x] Watch for response.warning, display warning as toast or banner
  - [x] Prevent infinite loader by showing fallback message
- [x] Fix Agent Dropdown: HAL + ASH Not Showing
  - [x] Check /api/agent/status response
  - [x] Fix frontend dropdown filter
  - [x] Add debug log for loaded agents
- [x] Eliminate vite.svg 404
  - [x] Remove <img src="/vite.svg" /> from layout files
  - [x] Replace with valid logo or nothing
  - [x] Prevent render loop caused by failed static asset fetch
