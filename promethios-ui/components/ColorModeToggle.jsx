import React from 'react';
import { useColorMode, Button, Flex } from '@chakra-ui/react';
import { MoonIcon, SunIcon } from '@chakra-ui/icons';

const ColorModeToggle = () => {
  const { colorMode, toggleColorMode } = useColorMode();
  
  return (
    <Flex justifyContent="flex-end" p={2}>
      <Button
        onClick={toggleColorMode}
        size="md"
        aria-label={`Toggle ${colorMode === 'light' ? 'Dark' : 'Light'} Mode`}
        variant="ghost"
        color={colorMode === 'light' ? 'gray.600' : 'gray.200'}
        _hover={{
          bg: colorMode === 'light' ? 'gray.100' : 'gray.700',
        }}
      >
        {colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
      </Button>
    </Flex>
  );
};

export default ColorModeToggle;
