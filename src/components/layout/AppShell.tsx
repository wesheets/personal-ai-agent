import { Box, Flex } from '@chakra-ui/react'
import Header from './Header'
import Sidebar from './Sidebar'
import Footer from './Footer'

interface AppShellProps {
  children: React.ReactNode
}

const AppShell: React.FC<AppShellProps> = ({ children }) => {
  return (
    <Flex direction="column" minH="100vh">
      <Header />
      <Flex flex="1">
        <Sidebar />
        <Box
          as="main"
          flex="1"
          p={4}
          ml={{ base: 0, md: 60 }}
          transition=".3s ease"
        >
          {children}
        </Box>
      </Flex>
      <Footer />
    </Flex>
  )
}

export default AppShell
