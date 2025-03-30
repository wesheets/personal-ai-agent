import { Box } from '@chakra-ui/react'
import MemoryBrowser from '../components/memory/MemoryBrowser'

const MemoryBrowserPage = () => {
  return (
    <Box pt={16} px={4} maxW="1200px" mx="auto">
      <MemoryBrowser />
    </Box>
  )
}

export default MemoryBrowserPage
