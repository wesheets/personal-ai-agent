import { extendTheme } from '@chakra-ui/react';

const config = {
  initialColorMode: 'system',
  useSystemColorMode: true
};

const colors = {
  brand: {
    50: '#e6f7ff',
    100: '#b3e0ff',
    200: '#80caff',
    300: '#4db3ff',
    400: '#1a9dff',
    500: '#0080ff',
    600: '#0066cc',
    700: '#004d99',
    800: '#003366',
    900: '#001a33'
  }
};

const styles = {
  global: (props) => ({
    body: {
      bg: props.colorMode === 'dark' ? 'gray.800' : 'gray.50',
      color: props.colorMode === 'dark' ? 'white' : 'gray.800'
    }
  })
};

const components = {
  Card: {
    baseStyle: (props) => ({
      container: {
        bg: props.colorMode === 'dark' ? 'gray.700' : 'white',
        boxShadow: 'md',
        borderRadius: 'lg',
        p: 4
      }
    })
  },
  Button: {
    variants: {
      primary: (props) => ({
        bg: props.colorMode === 'dark' ? 'brand.400' : 'brand.500',
        color: 'white',
        _hover: {
          bg: props.colorMode === 'dark' ? 'brand.500' : 'brand.600'
        }
      })
    }
  }
};

const theme = extendTheme({ config, colors, styles, components });

export default theme;
