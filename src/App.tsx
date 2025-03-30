import { Routes, Route } from 'react-router-dom'
import { Box } from '@chakra-ui/react'
import AppShell from './components/layout/AppShell'
import HomePage from './pages/HomePage'
import BuilderAgentPage from './pages/BuilderAgentPage'
import OpsAgentPage from './pages/OpsAgentPage'
import ResearchAgentPage from './pages/ResearchAgentPage'
import MemoryAgentPage from './pages/MemoryAgentPage'
import MemoryBrowserPage from './pages/MemoryBrowserPage'
import SettingsPage from './pages/SettingsPage'

function App() {
  return (
    <Box minH="100vh">
      <AppShell>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/agent/builder" element={<BuilderAgentPage />} />
          <Route path="/agent/ops" element={<OpsAgentPage />} />
          <Route path="/agent/research" element={<ResearchAgentPage />} />
          <Route path="/agent/memory" element={<MemoryAgentPage />} />
          <Route path="/memory" element={<MemoryBrowserPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </AppShell>
    </Box>
  )
}

export default App
