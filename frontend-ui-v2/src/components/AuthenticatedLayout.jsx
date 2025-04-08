import Sidebar from './Sidebar'
import { Box, Flex } from '@chakra-ui/react'

export default function AuthenticatedLayout({ children }) {
  return (
    <Flex>
      <Sidebar />
      <Box ml={{ base: 0, md: '60' }} p="4" pt="20" w="full">
        {children}
      </Box>
    </Flex>
  );
}
