import { extendTheme } from '@chakra-ui/react';

// Promethios brand colors
const colors = {
  brand: {
    50: '#f0f4ff',
    100: '#d9e2ff',
    200: '#b3c5ff',
    300: '#8da8ff',
    400: '#668bff',
    500: '#4a6ef5', // Primary brand color
    600: '#3a55d9',
    700: '#2a3eb3',
    800: '#1a278c',
    900: '#0a1066'
  },
  secondary: {
    50: '#fff0f4',
    100: '#ffd9e2',
    200: '#ffb3c5',
    300: '#ff8da8',
    400: '#ff668b',
    500: '#f54a6e', // Secondary brand color
    600: '#d93a55',
    700: '#b32a3e',
    800: '#8c1a27',
    900: '#660a10'
  },
  accent: {
    50: '#f0fff4',
    100: '#d9ffe2',
    200: '#b3ffc5',
    300: '#8dffa8',
    400: '#66ff8b',
    500: '#4af56e', // Accent brand color
    600: '#3ad955',
    700: '#2ab33e',
    800: '#1a8c27',
    900: '#0a6610'
  },
  neutral: {
    50: '#f7f7f7',
    100: '#e6e6e6',
    200: '#cccccc',
    300: '#b3b3b3',
    400: '#999999',
    500: '#808080',
    600: '#666666',
    700: '#4d4d4d',
    800: '#333333',
    900: '#1a1a1a'
  }
};

// Typography
const fonts = {
  heading: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif',
  body: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif',
  mono: '"Roboto Mono", SFMono-Regular, Menlo, Monaco, Consolas, monospace'
};

// Component styles
const components = {
  Button: {
    baseStyle: {
      fontWeight: 'semibold',
      borderRadius: 'md'
    },
    variants: {
      primary: {
        bg: 'brand.500',
        color: 'white',
        _hover: {
          bg: 'brand.600'
        },
        _active: {
          bg: 'brand.700'
        }
      },
      secondary: {
        bg: 'secondary.500',
        color: 'white',
        _hover: {
          bg: 'secondary.600'
        },
        _active: {
          bg: 'secondary.700'
        }
      },
      accent: {
        bg: 'accent.500',
        color: 'white',
        _hover: {
          bg: 'accent.600'
        },
        _active: {
          bg: 'accent.700'
        }
      },
      outline: {
        borderColor: 'brand.500',
        color: 'brand.500',
        _hover: {
          bg: 'brand.50'
        },
        _active: {
          bg: 'brand.100'
        }
      }
    },
    defaultProps: {
      variant: 'primary'
    }
  },
  Heading: {
    baseStyle: {
      fontWeight: 'bold',
      color: 'neutral.800'
    }
  },
  Card: {
    baseStyle: {
      p: 4,
      borderRadius: 'md',
      boxShadow: 'md',
      bg: 'white'
    }
  },
  Badge: {
    baseStyle: {
      borderRadius: 'full',
      px: 2,
      py: 1,
      fontWeight: 'medium'
    },
    variants: {
      brand: {
        bg: 'brand.100',
        color: 'brand.800'
      },
      secondary: {
        bg: 'secondary.100',
        color: 'secondary.800'
      },
      accent: {
        bg: 'accent.100',
        color: 'accent.800'
      }
    },
    defaultProps: {
      variant: 'brand'
    }
  },
  Link: {
    baseStyle: {
      color: 'brand.500',
      _hover: {
        textDecoration: 'underline',
        color: 'brand.600'
      }
    }
  }
};

// Global styles
const styles = {
  global: {
    body: {
      bg: 'gray.50',
      color: 'neutral.800'
    },
    a: {
      color: 'brand.500',
      _hover: {
        textDecoration: 'underline'
      }
    }
  }
};

// Breakpoints
const breakpoints = {
  sm: '30em',
  md: '48em',
  lg: '62em',
  xl: '80em',
  '2xl': '96em'
};

// Create the theme
const brandTheme = extendTheme({
  colors,
  fonts,
  components,
  styles,
  breakpoints,
  config: {
    initialColorMode: 'light',
    useSystemColorMode: false
  }
});

export default brandTheme;
