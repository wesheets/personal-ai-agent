import { Box, Text, Flex, Link } from '@chakra-ui/react'

const Footer = () => {
  return (
    <Box
      as="footer"
      py={4}
      px={6}
      bg="white"
      borderTop="1px"
      borderTopColor="gray.200"
      sx={{
        _dark: { 
          bg: 'gray.800',
          borderTopColor: 'gray.700' 
        }
      }}
    >
      <Flex justify="space-between" align="center">
        <Text fontSize="sm" color="gray.500">
          Personal AI Agent System &copy; {new Date().getFullYear()}
        </Text>
        <Flex gap={4}>
          <Link href="#" fontSize="sm" color="gray.500">
            Documentation
          </Link>
          <Link href="#" fontSize="sm" color="gray.500">
            GitHub
          </Link>
        </Flex>
      </Flex>
    </Box>
  )
}

export default Footer
