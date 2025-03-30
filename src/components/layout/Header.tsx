import { Flex, Heading, Spacer, Button, useColorMode, IconButton } from '@chakra-ui/react'
import { MoonIcon, SunIcon } from '@chakra-ui/icons'

const Header = () => {
  const { colorMode, toggleColorMode } = useColorMode()
  
  return (
    <Flex
      as="header"
      position="fixed"
      top="0"
      width="full"
      shadow="sm"
      py={4}
      px={6}
      bg="white"
      _dark={{ bg: 'gray.800' }}
      zIndex="banner"
    >
      <Flex align="center">
        <Heading size="md">Personal AI Agent</Heading>
      </Flex>
      <Spacer />
      <Flex>
        <IconButton
          aria-label={`Switch to ${colorMode === 'light' ? 'dark' : 'light'} mode`}
          variant="ghost"
          color="current"
          ml={3}
          fontSize="lg"
          onClick={toggleColorMode}
          icon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
        />
        <Button variant="ghost" ml={3}>Settings</Button>
      </Flex>
    </Flex>
  )
}

export default Header
